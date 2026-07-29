from __future__ import annotations

from pathlib import Path
from typing import Any


class FileParser:
    """Simple parser that extracts text-like content from uploaded files for demo purposes."""

    def parse(self, file_path: str | Path) -> dict[str, Any]:
        path = Path(file_path)
        text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        return {
            "filename": path.name,
            "size_bytes": path.stat().st_size if path.exists() else 0,
            "sample_text": text[:400].strip(),
            "parsed": bool(text.strip()),
        }
