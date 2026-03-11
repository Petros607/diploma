# tests/test_parser.py

"""Интеграционный тест"""

import pytest
from app.services.summary_service import SummaryService

@pytest.fixture
def service():
    return SummaryService()


@pytest.fixture
def speeches_folder():
    return "./data/test/"


def test_summarize(service, speeches_folder):
    filename = "speech1.txt"
    result = service.summarize_from_file(f"{speeches_folder}{filename}")
    print("\nКонспект:")
    print(result)

