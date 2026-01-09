import sqlite3
import json
from typing import List
from .models import Job, Account

class PersistenceManager:
    def __init__(self, db_path="sora_manager.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY, created_at REAL, status TEXT, prompt_text TEXT,
                dedup_hash TEXT, account_id TEXT, external_sora_id TEXT, download_path TEXT,
                next_retry_at REAL, retry_count INTEGER, error_log TEXT, metadata TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY, status TEXT, cookie_bundle TEXT, quota_daily_limit INTEGER,
                quota_used_today INTEGER, last_used_at REAL, cooldown_until REAL,
                last_quota_error REAL, consecutive_failures INTEGER
            )
        """)
        conn.commit()
        conn.close()

    def save_job(self, job: Job):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("INSERT OR REPLACE INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (job.id, job.created_at, job.status, job.prompt_text, job.dedup_hash,
                 job.account_id, job.external_sora_id, job.download_path, job.next_retry_at,
                 job.retry_count, json.dumps(job.error_log), json.dumps(job.metadata)))
            conn.commit()
        finally:
            conn.close()

    def load_all_jobs(self) -> List[Job]:
        conn = sqlite3.connect(self.db_path)
        jobs = []
        try:
            for row in conn.execute("SELECT * FROM jobs"):
                jobs.append(Job(id=row[0], created_at=row[1], status=row[2], prompt_text=row[3],
                    dedup_hash=row[4], account_id=row[5], external_sora_id=row[6], download_path=row[7],
                    next_retry_at=row[8], retry_count=row[9], error_log=json.loads(row[10]), metadata=json.loads(row[11])))
        finally:
            conn.close()
        return jobs

    def save_account(self, account: Account):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("INSERT OR REPLACE INTO accounts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (account.id, account.status, account.cookie_bundle, account.quota_daily_limit,
                 account.quota_used_today, account.last_used_at, account.cooldown_until,
                 account.last_quota_error, account.consecutive_failures))
            conn.commit()
        finally:
            conn.close()

    def load_all_accounts(self) -> List[Account]:
        conn = sqlite3.connect(self.db_path)
        accounts = []
        try:
            for row in conn.execute("SELECT * FROM accounts"):
                accounts.append(Account(id=row[0], status=row[1], cookie_bundle=row[2],
                    quota_daily_limit=row[3], quota_used_today=row[4], last_used_at=row[5],
                    cooldown_until=row[6], last_quota_error=row[7], consecutive_failures=row[8]))
        finally:
            conn.close()
        return accounts
