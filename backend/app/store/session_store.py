"""In-memory session store for analysis jobs with TTL expiry."""

from __future__ import annotations

from datetime import datetime, timezone

from app.models.analysis import AnalysisResult


class SessionStore:
    """Ephemeral job store keyed by job_id (UUID)."""

    def __init__(self) -> None:
        self._jobs: dict[str, AnalysisResult] = {}

    def save(self, result: AnalysisResult) -> AnalysisResult:
        self.purge_expired()
        self._jobs[result.job_id] = result
        return result

    def get(self, job_id: str) -> AnalysisResult | None:
        self.purge_expired()
        result = self._jobs.get(job_id)
        if result is None:
            return None
        if result.expires_at < datetime.now(timezone.utc):
            self._jobs.pop(job_id, None)
            return None
        return result

    def delete(self, job_id: str) -> bool:
        if job_id in self._jobs:
            del self._jobs[job_id]
            return True
        return False

    def purge_expired(self) -> int:
        now = datetime.now(timezone.utc)
        expired = [jid for jid, job in self._jobs.items() if job.expires_at < now]
        for jid in expired:
            del self._jobs[jid]
        return len(expired)

    def count(self) -> int:
        return len(self._jobs)


# Module-level singleton for prototype
session_store = SessionStore()
