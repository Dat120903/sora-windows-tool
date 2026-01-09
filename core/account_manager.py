import time
from typing import Optional, List
from .models import Account, AccountStatus
from .persistence import PersistenceManager

class AccountManager:
    def __init__(self, persistence: PersistenceManager):
        self.persistence = persistence
        self.accounts: List[Account] = self.persistence.load_all_accounts()

    def add_account(self, cookie_bundle: str, account_id: str):
        account = Account(id=account_id, cookie_bundle=cookie_bundle)
        self.accounts.append(account)
        self.persistence.save_account(account)

    def get_best_available_account(self) -> Optional[Account]:
        now = time.time()
        candidates = []
        for acc in self.accounts:
            if acc.status == AccountStatus.INVALID.value:
                continue
            if acc.status == AccountStatus.COOLDOWN.value:
                if now < acc.cooldown_until:
                    continue
                else:
                    acc.status = AccountStatus.ACTIVE.value
                    acc.cooldown_until = 0
                    self.persistence.save_account(acc)
            if acc.status == AccountStatus.SOFT_BANNED.value:
                if now - acc.last_used_at < 3600:
                    continue
            if acc.quota_used_today >= acc.quota_daily_limit:
                 if acc.status != AccountStatus.WAITING_RECOVERY.value:
                     acc.status = AccountStatus.WAITING_RECOVERY.value
                     self.persistence.save_account(acc)
                 continue
            candidates.append(acc)
        if not candidates:
            return None
        candidates.sort(key=lambda x: (x.quota_used_today, x.last_used_at))
        return candidates[0]

    def mark_account_used(self, account_id: str):
        acc = self._get_account(account_id)
        if acc:
            acc.last_used_at = time.time()
            acc.quota_used_today += 1
            self.persistence.save_account(acc)

    def handle_error(self, account_id: str, error_code: int):
        acc = self._get_account(account_id)
        if not acc:
            return
        if error_code == 401:
            acc.status = AccountStatus.INVALID.value
        elif error_code == 429:
            acc.status = AccountStatus.COOLDOWN.value
            backoff_seconds = 1800 * (2 ** acc.consecutive_failures)
            acc.cooldown_until = time.time() + backoff_seconds
            acc.consecutive_failures += 1
            acc.last_quota_error = time.time()
            acc.quota_daily_limit = max(1, acc.quota_used_today)
        self.persistence.save_account(acc)

    def handle_success(self, account_id: str):
        acc = self._get_account(account_id)
        if acc:
            acc.consecutive_failures = 0
            self.persistence.save_account(acc)

    def _get_account(self, account_id: str) -> Optional[Account]:
        for acc in self.accounts:
            if acc.id == account_id:
                return acc
        return None
