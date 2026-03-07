# tests/0_test_parser.py
"""Интеграционный тест"""
import pytest
from app.services.parser_service import ParserService
from tabulate import tabulate


@pytest.fixture
def parser():
    return ParserService()

def test_get_data(parser):
    url = "https://bbb.ssau.ru:8443/playback/presentation/2.3/097c80a16ee9277077ca6a347f6e8f9c597b9a62-1772091088848"
    slides_url = parser.get_data(url)
    assert slides_url.startswith("https://bbb.ssau.ru:8443/presentation/")
    assert "&" in slides_url

def test_download_image(parser):
    slides_url = "https://bbb.ssau.ru:8443/presentation/097c80a16ee9277077ca6a347f6e8f9c597b9a62-1772091088848/presentation/7019735ea8f4afd8732a84dea84f88aff48a14fc-1772091192876/svgs/slide&7019735ea8f4afd8732a84dea84f88aff48a14fc-1772091192876"
    slides_path = parser.download_image(slides_url)
    assert slides_path.exists()
    assert any(slides_path.iterdir())

def test_download_audio(parser):
    slides_url = "https://bbb.ssau.ru:8443/presentation/097c80a16ee9277077ca6a347f6e8f9c597b9a62-1772091088848/presentation/7019735ea8f4afd8732a84dea84f88aff48a14fc-1772091192876/svgs/slide&7019735ea8f4afd8732a84dea84f88aff48a14fc-1772091192876"
    audio_path = parser.download_audio(slides_url)
    length = parser.get_length(str(audio_path))
    print(f"Длина аудио: {length} секунд")
    assert length > 0
    assert isinstance(length, float)
    assert audio_path.exists()
    assert audio_path.name == "lecture.webm"

def test_get_metadata(parser):
    url = "https://bbb.ssau.ru/b/zat-vdd-mdu"

    metadata = parser.get_metadata(url)
    print(f"Metadata for {url}: \n{metadata}")

    assert isinstance(metadata, dict)
    assert len(metadata) > 0

def test_get_metadata_multiple(parser):

    expected_counts = {
        "https://bbb.ssau.ru/b/zat-vdd-mdu": 1,  # Одна страница (хотя бы 1 запись)
        "https://bbb.ssau.ru/b/wgd-w68-zyv-lwn": 0,  # Нет записей
        "https://bbb.ssau.ru/b/arc-gu6-rcm": 25  # Несколько страниц (ожидаем 25 записей)
    }

    parser = ParserService()

    for url in expected_counts.keys():
        metadata = parser.get_metadata(url)
        actual_count = len(metadata)
        expected_count = expected_counts[url]

        assert expected_count <= actual_count, \
            f"Для URL {url} ожидалось не менее {expected_count} лекций, получено {actual_count}"
        
        rows = []
        for i, item in enumerate(metadata.values()):
            rows.append([
                i,
                item["name_subject"],
                item["name_teacher"],
                item["datetime"],
                item["url"],
                item["length"],
                item["users_count"]
            ])

        print("\nURL:", url)
        print("Всего лекций:", len(rows))

        print(tabulate(
            rows,
            headers=["#", "Subject", "Teacher", "Datetime", "URL", "Length", "Users"],
            tablefmt="github"
        ))
