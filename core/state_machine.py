import time
import os
from .models import Job, JobStatus, AccountStatus
from .account_manager import AccountManager
from .mock_sora_client import MockSoraClient
from .persistence import PersistenceManager

class JobStateMachine:
    def __init__(self, persistence: PersistenceManager, account_manager: AccountManager, sora_client: MockSoraClient):
        self.persistence = persistence
        self.account_manager = account_manager
        self.sora_client = sora_client

    def process_tick(self, job: Job):
        try:
            self._handle_state(job)
        except Exception as e:
            if job.status not in [JobStatus.FAILED.value, JobStatus.DONE.value]:
                job.error_log.append(str(e))
                self._schedule_retry(job)

    def _handle_state(self, job: Job):
        status = job.status
        if status == JobStatus.QUEUED.value:
            account = self.account_manager.get_best_available_account()
            if account:
                job.account_id = account.id
                self._transition(job, JobStatus.ASSIGNED_ACCOUNT)
            else:
                self._transition(job, JobStatus.WAITING_FOR_ACCOUNT)
        elif status == JobStatus.WAITING_FOR_ACCOUNT.value:
            account = self.account_manager.get_best_available_account()
            if account:
                job.account_id = account.id
                self._transition(job, JobStatus.ASSIGNED_ACCOUNT)
        elif status == JobStatus.ASSIGNED_ACCOUNT.value:
            try:
                account = self.account_manager._get_account(job.account_id)
                if not account:
                    self._transition(job, JobStatus.QUEUED)
                    return
                ext_id = self.sora_client.create_video(account.cookie_bundle, job.prompt_text)
                job.external_sora_id = ext_id
                self.account_manager.mark_account_used(account.id)
                self.account_manager.handle_success(account.id)
                self._transition(job, JobStatus.CREATING_VIDEO)
                self._transition(job, JobStatus.POLLING_STATUS)
            except Exception as e:
                self._handle_api_error(job, e)
        elif status == JobStatus.POLLING_STATUS.value:
            try:
                status_remote = self.sora_client.get_status(job.external_sora_id)
                if status_remote == "finished":
                    self._transition(job, JobStatus.DOWNLOADING)
                elif status_remote == "failed":
                    self._transition(job, JobStatus.FAILED)
            except Exception as e:
                self._handle_api_error(job, e)
        elif status == JobStatus.DOWNLOADING.value:
            try:
                os.makedirs("downloads", exist_ok=True)
                path = f"downloads/{job.id}.mp4"
                self.sora_client.download_video(job.external_sora_id, path)
                job.download_path = path
                self._transition(job, JobStatus.DONE)
            except Exception as e:
                self._handle_api_error(job, e)
        elif status == JobStatus.RETRY_SCHEDULED.value:
            if time.time() > job.next_retry_at:
                job.status = JobStatus.QUEUED.value
                self.persistence.save_job(job)

    def _transition(self, job: Job, new_status: JobStatus):
        job.status = new_status.value
        self.persistence.save_job(job)

    def _handle_api_error(self, job: Job, error: Exception):
        msg = str(error)
        job.error_log.append(msg)
        if "401" in msg:
            self.account_manager.handle_error(job.account_id, 401)
            job.account_id = None
            self._schedule_retry(job)
        elif "429" in msg:
            self.account_manager.handle_error(job.account_id, 429)
            job.account_id = None
            self._schedule_retry(job)
        else:
            self._schedule_retry(job)

    def _schedule_retry(self, job: Job):
        job.retry_count += 1
        if job.retry_count > 5:
            self._transition(job, JobStatus.FAILED)
        else:
            job.next_retry_at = time.time() + (2 ** job.retry_count)
            self._transition(job, JobStatus.RETRY_SCHEDULED)
