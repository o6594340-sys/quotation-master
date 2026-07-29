from __future__ import annotations

from pathlib import Path
from typing import Any

from app.services.estimate_builder import EstimateBuilder
from app.services.export_service import ExportService
from app.services.file_parser import FileParser


class QuotationService:
    """In-memory job service with simple persistence hooks for the MVP."""

    def __init__(self, storage_dir: str | None = None) -> None:
        self._jobs: dict[str, dict[str, Any]] = {}
        self.storage_dir = Path(storage_dir) if storage_dir is not None else None
        self._estimate_builder = EstimateBuilder()
        self._export_service = ExportService(str(self.storage_dir / "exports") if self.storage_dir is not None else None)
        self._file_parser = FileParser()
        if self.storage_dir is not None:
            self.storage_dir.mkdir(parents=True, exist_ok=True)

    def create_job(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        job_id = f"job-{len(self._jobs) + 1:03d}"
        output_language = payload.get("output_language", "keep_english")
        translation_mode = (
            "natural_russian"
            if output_language == "translate_russian"
            else "preserve_source"
        )

        parsed_files = []
        for source in payload.get("sources", []):
            parsed_files.append(self._file_parser.parse(str(source)))

        estimate = self._estimate_builder.build(payload)
        export_paths = {
            "json": str(self._export_service.export_json(job_id, estimate)),
            "csv": str(self._export_service.export_csv(job_id, estimate)),
        }
        job = {
            "id": job_id,
            "status": "received",
            "source_count": len(payload.get("sources", [])),
            "strategy": payload.get("strategy", "lowest_price"),
            "output_language": output_language,
            "translation_mode": translation_mode,
            "uploaded_files": [str(item) for item in payload.get("sources", [])],
            "parsed_files": parsed_files,
            "estimate": estimate,
            "exports": export_paths,
            "message": (
                "Job accepted and ready for processing. "
                "Russian output will use a natural, polished translation style."
                if output_language == "translate_russian"
                else "Job accepted and ready for processing. The estimate will stay in the selected source language."
            ),
        }
        self._jobs[job_id] = job
        return job

    def get_job_status(self, job_id: str) -> dict[str, Any] | None:
        return self._jobs.get(job_id)

    def update_job_status(self, job_id: str, status: str, **kwargs: Any) -> dict[str, Any] | None:
        job = self._jobs.get(job_id)
        if job is None:
            return None

        progress = kwargs.get("progress")
        if progress is not None:
            job["progress"] = progress
        job.update({"status": status, **kwargs})
        return job


SERVICE = QuotationService()


def create_job(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return SERVICE.create_job(payload)


def get_job_status(job_id: str) -> dict[str, Any] | None:
    return SERVICE.get_job_status(job_id)


def update_job_status(job_id: str, status: str, **kwargs: Any) -> dict[str, Any] | None:
    return SERVICE.update_job_status(job_id, status, **kwargs)
