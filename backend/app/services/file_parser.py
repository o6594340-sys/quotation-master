from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


class FileParser:
    """Parse text-like uploads from simple file formats for the MVP demo."""

    def parse(self, file_path: str | Path) -> dict[str, Any]:
        path = Path(file_path)
        if not path.exists():
            return {
                "filename": path.name,
                "size_bytes": 0,
                "sample_text": "",
                "parsed": False,
            }

        suffix = path.suffix.lower()
        if suffix == ".csv":
            return self._parse_csv(path)
        if suffix == ".json":
            return self._parse_json(path)
        return self._parse_text(path)

    def _parse_text(self, path: Path) -> dict[str, Any]:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return {
            "filename": path.name,
            "size_bytes": path.stat().st_size,
            "sample_text": text[:400].strip(),
            "parsed": bool(text.strip()),
            "format": "text",
        }

    def _parse_csv(self, path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
            rows = list(csv.reader(handle))
        sample_rows = rows[:3]
        return {
            "filename": path.name,
            "size_bytes": path.stat().st_size,
            "sample_text": " | ".join(" | ".join(row) for row in sample_rows),
            "parsed": bool(rows),
            "format": "csv",
            "row_count": len(rows),
        }

    def _parse_json(self, path: Path) -> dict[str, Any]:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        if isinstance(data, dict):
            preview = {key: data[key] for key in list(data.keys())[:3]}
        else:
            preview = data[:3] if isinstance(data, list) else data
        return {
            "filename": path.name,
            "size_bytes": path.stat().st_size,
            "sample_text": json.dumps(preview, ensure_ascii=False)[:400],
            "parsed": True,
            "format": "json",
        }
