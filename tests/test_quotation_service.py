import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.services.quotation_service import QuotationService


class QuotationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.service = QuotationService(storage_dir=self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

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
