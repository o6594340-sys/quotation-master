from __future__ import annotations

from typing import Any


JOBS: dict[str, dict[str, Any]] = {}


def create_job(payload: dict[str, Any]) -> dict[str, Any]:
    """Create a placeholder job for the MVP skeleton."""
    job_id = f"job-{len(JOBS) + 1:03d}"
    job = {
        "id": job_id,
        "status": "received",
        "source_count": len(payload.get("sources", [])),
        "strategy": payload.get("strategy", "lowest_price"),
        "message": "Job accepted and ready for processing.",
    }
    JOBS[job_id] = job
    return job


def get_job_status(job_id: str) -> dict[str, Any] | None:
    """Return the current state of a job or None when missing."""
    return JOBS.get(job_id)
