# tests/1_test_speech_service.py

"""Интеграционный тест"""

import pytest
from app.services.speech_service import SpeechService

@pytest.fixture
def service():
    return SpeechService()


@pytest.fixture
def speeches_folder():
    return "./data/test/"


def test_transcription(service, speeches_folder):
    filename = "speech1.mp3"
    result = service.transcribe(f"{speeches_folder}{filename}")
    print("\nРаспознанный текст:")
    print(result)
