import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.services.quotation_service import QuotationService


class QuotationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.service = QuotationService(storage_dir=self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _write_docx(self, path: Path, text: str) -> None:
        content_types = """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">
  <Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>
  <Default Extension=\"xml\" ContentType=\"application/xml\"/>
  <Override PartName=\"/word/document.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml\"/>
</Types>"""
        rels = """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
  <Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"word/document.xml\"/>
</Relationships>"""
        document = f"""<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">
  <w:body>
    <w:p><w:r><w:t>{text}</w:t></w:r></w:p>
    <w:sectPr/></w:body>
</w:document>"""
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("[Content_Types].xml", content_types)
            archive.writestr("_rels/.rels", rels)
            archive.writestr("word/document.xml", document)

    def _write_xlsx(self, path: Path, rows: list[list[str]]) -> None:
        shared_strings: list[str] = []
        index_by_value: dict[str, int] = {}
        for row in rows:
            for value in row:
                if value not in index_by_value:
                    index_by_value[value] = len(shared_strings)
                    shared_strings.append(value)

        items = "".join(f"<si><t>{value}</t></si>" for value in shared_strings)
        shared_strings_xml = f"""<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<sst xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" count=\"{len(shared_strings)}\" uniqueCount=\"{len(shared_strings)}\">
{items}
</sst>"""

        sheet_rows = []
        for row_index, row in enumerate(rows, start=1):
            cells = []
            for col_index, value in enumerate(row, start=1):
                index = index_by_value[value]
                cell_ref = f"{chr(64 + col_index)}{row_index}"
                cells.append(f"<c r=\"{cell_ref}\" t=\"s\"><v>{index}</v></c>")
            sheet_rows.append(f"<row r=\"{row_index}\">{''.join(cells)}</row>")

        sheet = f"""<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <sheetData>
    {''.join(sheet_rows)}
  </sheetData>
</worksheet>"""

        content_types = """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">
  <Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>
  <Default Extension=\"xml\" ContentType=\"application/xml\"/>
  <Override PartName=\"/xl/workbook.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/>
  <Override PartName=\"/xl/worksheets/sheet1.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/>
  <Override PartName=\"/xl/sharedStrings.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml\"/>
</Types>"""
        rels = """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
  <Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"xl/workbook.xml\"/>
</Relationships>"""
        workbook = """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\">
  <sheets>
    <sheet name=\"Sheet1\" sheetId=\"1\" r:id=\"rId1\"/>
  </sheets>
</workbook>"""
        rels2 = """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
  <Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet1.xml\"/>
  <Relationship Id=\"rId2\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings\" Target=\"sharedStrings.xml\"/>
</Relationships>"""
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("[Content_Types].xml", content_types)
            archive.writestr("_rels/.rels", rels)
            archive.writestr("xl/workbook.xml", workbook)
            archive.writestr("xl/_rels/workbook.xml.rels", rels2)
            archive.writestr("xl/worksheets/sheet1.xml", sheet)
            archive.writestr("xl/sharedStrings.xml", shared_strings_xml)

    def test_create_job_records_uploaded_files(self) -> None:
        job = self.service.create_job({"sources": ["a.pdf", "b.xlsx"], "strategy": "lowest_price"})

        self.assertEqual(job["status"], "received")
        self.assertEqual(job["uploaded_files"], ["a.pdf", "b.xlsx"])
        self.assertEqual(self.service.get_job_status(job["id"])["uploaded_files"], ["a.pdf", "b.xlsx"])

    def test_update_job_status(self) -> None:
        job = self.service.create_job({})

        updated = self.service.update_job_status(job["id"], "processing", progress=25)

        self.assertEqual(updated["status"], "processing")
        self.assertEqual(updated["progress"], 25)

    def test_create_job_extracts_text_from_docx(self) -> None:
        docx_path = Path(self.tempdir.name) / "brief.docx"
        self._write_docx(docx_path, "Annual Gala venue")

        job = self.service.create_job({"sources": [str(docx_path)]})
        parsed = job["parsed_files"][0]

        self.assertEqual(parsed["format"], "docx")
        self.assertIn("Annual Gala venue", parsed["sample_text"])
        self.assertTrue(parsed["parsed"])

    def test_create_job_extracts_text_from_xlsx(self) -> None:
        xlsx_path = Path(self.tempdir.name) / "pricing.xlsx"
        self._write_xlsx(xlsx_path, [["Service", "Price"], ["Coffee break", "1500"]])

        job = self.service.create_job({"sources": [str(xlsx_path)]})
        parsed = job["parsed_files"][0]

        self.assertEqual(parsed["format"], "xlsx")
        self.assertIn("Coffee break", parsed["sample_text"])
        self.assertTrue(parsed["parsed"])

    def test_create_job_builds_estimate_preview_for_russian_output(self) -> None:
        job = self.service.create_job({
            "sources": ["quote.pdf"],
            "strategy": "lowest_price",
            "output_language": "translate_russian",
        })

        estimate = job["estimate"]
        self.assertEqual(estimate["title"], "Смета по программе")
        self.assertEqual(estimate["items"][0]["category"], "Размещение")
        self.assertGreaterEqual(estimate["total"], 0)

    def test_create_job_uses_agency_template_metadata(self) -> None:
        agency_template = {
            "name": "agency_alpha",
            "title_english": "Agency Alpha Proposal",
            "subtitle_english": "Prepared in agency format",
            "title_russian": "Коммерческое предложение Agency Alpha",
            "subtitle_russian": "Подготовлено по формату агентства",
            "section_name": "Program Cost",
        }

        job = self.service.create_job({
            "sources": ["quote.pdf"],
            "agency_template": agency_template,
            "output_language": "keep_english",
        })

        estimate = job["estimate"]
        self.assertEqual(estimate["title"], "Agency Alpha Proposal")
        self.assertEqual(estimate["template"]["name"], "agency_alpha")
        self.assertEqual(estimate["items"][0]["section"], "Program Cost")
