from typing import List
from .models import Job, JobStatus
from .persistence import PersistenceManager

class QueueEngine:
    def __init__(self, persistence: PersistenceManager):
        self.persistence = persistence
        self.jobs = self.persistence.load_all_jobs()

    def add_job(self, prompt_text: str) -> Job:
        job = Job(prompt_text=prompt_text)
        job.status = JobStatus.QUEUED.value  # Move to QUEUED immediately
        self.jobs.append(job)
        self.persistence.save_job(job)
        return job

    def get_job(self, job_id: str) -> Job:
        for job in self.jobs:
            if job.id == job_id:
                return job
        return None

    def get_active_jobs(self) -> List[Job]:
        active_states = [JobStatus.QUEUED.value, JobStatus.WAITING_FOR_ACCOUNT.value, 
            JobStatus.ASSIGNED_ACCOUNT.value, JobStatus.CREATING_VIDEO.value,
            JobStatus.POLLING_STATUS.value, JobStatus.RETRY_SCHEDULED.value, JobStatus.DOWNLOADING.value]
        return [j for j in self.jobs if j.status in active_states]

    def get_all_jobs(self) -> List[Job]:
        return self.jobs
