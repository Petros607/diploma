# tests/2_test_summary_service.py

"""Интеграционный тест"""

import pytest
from pathlib import Path

from app.services.pdf_service import PdfService

@pytest.fixture
def service():
    return PdfService()


@pytest.fixture
def test_folder():
    return Path("./data/test/")


@pytest.mark.asyncio
async def test_generate_pdf(service, test_folder):

    summary_file = test_folder / "speech2_summary.txt"
    slides_dir = test_folder / "presentation2"
    output_file = test_folder / "speech2_lecture.pdf"

    result_path = await service.generate_pdf_from_summary(
        summary_path=str(summary_file),
        slides_dir=str(slides_dir),
        output_path=str(output_file)
    )

    pdf_path = Path(result_path)
    assert pdf_path.exists()
    size = pdf_path.stat().st_size
    print("\nPDF size:", size)
    assert size > 0
