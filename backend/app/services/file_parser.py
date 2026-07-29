from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET


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
        if suffix == ".docx":
            return self._parse_docx(path)
        if suffix == ".xlsx":
            return self._parse_xlsx(path)
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

    def _parse_docx(self, path: Path) -> dict[str, Any]:
        text = self._extract_docx_text(path)
        return {
            "filename": path.name,
            "size_bytes": path.stat().st_size,
            "sample_text": text[:400].strip(),
            "parsed": bool(text.strip()),
            "format": "docx",
        }

    def _extract_docx_text(self, path: Path) -> str:
        with zipfile.ZipFile(path) as archive:
            try:
                document_xml = archive.read("word/document.xml")
            except KeyError:
                return ""

        root = ET.fromstring(document_xml)
        namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        texts = [node.text or "" for node in root.findall(".//w:t", namespace)]
        return "\n".join(text for text in texts if text)

    def _parse_xlsx(self, path: Path) -> dict[str, Any]:
        text = self._extract_xlsx_text(path)
        return {
            "filename": path.name,
            "size_bytes": path.stat().st_size,
            "sample_text": text[:400].strip(),
            "parsed": bool(text.strip()),
            "format": "xlsx",
        }

    def _extract_xlsx_text(self, path: Path) -> str:
        with zipfile.ZipFile(path) as archive:
            shared_strings: list[str] = []
            if "xl/sharedStrings.xml" in archive.namelist():
                shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
                namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
                for item in shared_root.findall("main:si", namespace):
                    values = [node.text or "" for node in item.findall(".//main:t", namespace)]
                    shared_strings.append("".join(values))

            sheet_root = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))

        namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        rows: list[list[str]] = []
        for row in sheet_root.findall(".//main:sheetData/main:row", namespace):
            values: list[str] = []
            for cell in row.findall("main:c", namespace):
                cell_type = cell.get("t")
                raw_value = cell.findtext("main:v", default="", namespaces=namespace)
                if cell_type == "s" and raw_value:
                    index = int(raw_value)
                    values.append(shared_strings[index] if index < len(shared_strings) else "")
                else:
                    values.append(raw_value)
            rows.append(values)

        return " | ".join(" | ".join(row) for row in rows if row)
