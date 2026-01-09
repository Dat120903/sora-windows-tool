import uuid
import time
import hashlib
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict

class JobStatus(Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    WAITING_FOR_ACCOUNT = "WAITING_FOR_ACCOUNT"
    ASSIGNED_ACCOUNT = "ASSIGNED_ACCOUNT"
    CREATING_VIDEO = "CREATING_VIDEO"
    POLLING_STATUS = "POLLING_STATUS"
    RETRY_SCHEDULED = "RETRY_SCHEDULED"
    DOWNLOADING = "DOWNLOADING"
    DONE = "DONE"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class AccountStatus(Enum):
    ACTIVE = "ACTIVE"
    WAITING_RECOVERY = "WAITING_RECOVERY"
    SOFT_BANNED = "SOFT_BANNED"
    COOLDOWN = "COOLDOWN"
    INVALID = "INVALID"

@dataclass
class Job:
    prompt_text: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    status: str = JobStatus.CREATED.value
    dedup_hash: str = ""
    account_id: Optional[str] = None
    external_sora_id: Optional[str] = None
    download_path: Optional[str] = None
    next_retry_at: float = 0.0
    retry_count: int = 0
    error_log: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.dedup_hash:
            content = f"{self.prompt_text}"
            self.dedup_hash = hashlib.sha256(content.encode()).hexdigest()

@dataclass
class Account:
    id: str
    cookie_bundle: str = ""
    status: str = AccountStatus.ACTIVE.value
    quota_daily_limit: int = 10
    quota_used_today: int = 0
    last_used_at: float = 0.0
    cooldown_until: float = 0.0
    last_quota_error: float = 0.0
    consecutive_failures: int = 0
