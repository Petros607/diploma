# tests/2_test_summary_service.py

"""Интеграционный тест"""

import pytest
from pathlib import Path

from app.services.summary_service import SummaryService

@pytest.fixture
def service():
    return SummaryService()


@pytest.fixture
def speeches_folder():
    return "./data/test/"


@pytest.fixture
def slide_timings():
    """
    Пример таймингов переключения слайдов
    секунда -> номер слайда
    """
    #https://bbb.ssau.ru/b/arc-gu6-rcm
    #https://bbb.ssau.ru:8443/playback/presentation/2.3/097c80a16ee9277077ca6a347f6e8f9c597b9a62-1759998690614
    return {"0": 23, "216": 24, "360": 25, "534": 26, "769": 27, "862": 28, "903": 29, "980": 30, "1091": 31, "1241": 32, "1386": 33, "1533": 34, "1607": 35, "1729": 36, "1773": 37, "1792": 38, "1822": 39, "2007": 40, "2140": 41, "2185": 42}


@pytest.mark.asyncio
async def test_summarize(service, speeches_folder, slide_timings):
    filename = "speech2"
    transcript_file = f"{speeches_folder}{filename}.txt"
    output_file = f"{speeches_folder}{filename}_summary.txt"
    result_path = await service.summarize_from_file(
        transcript_path=transcript_file,
        slide_timings=slide_timings,
        output_path=output_file
    )
    path = Path(result_path)
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert len(text) > 0
