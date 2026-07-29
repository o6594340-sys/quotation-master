from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


class ExportService:
    """Create a simple export artifact for the generated estimate."""

    def __init__(self, output_dir: str | None = None) -> None:
        self.output_dir = Path(output_dir) if output_dir is not None else None
        if self.output_dir is not None:
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_json(self, job_id: str, estimate: dict[str, Any]) -> Path:
        target_dir = self.output_dir or Path.cwd() / "exports"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{job_id}.json"
        target_path.write_text(json.dumps(estimate, indent=2, ensure_ascii=False), encoding="utf-8")
        return target_path

    def export_csv(self, job_id: str, estimate: dict[str, Any]) -> Path:
        target_dir = self.output_dir or Path.cwd() / "exports"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{job_id}.csv"
        with target_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["category", "description", "amount", "source"])
            for item in estimate.get("items", []):
                writer.writerow([item.get("category"), item.get("description"), item.get("amount"), item.get("source")])
        return target_path
