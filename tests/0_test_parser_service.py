# tests/0_test_parser_service.py

"""Интеграционный тест"""

import pytest
from tabulate import tabulate
from app.services.parser_service import ParserService


@pytest.fixture
def parser():
    return ParserService()


@pytest.fixture
def lecture_url():
    return "https://bbb.ssau.ru:8443/playback/presentation/2.3/bc140f637937d69f1ce2f7b836745e4c24131f16-1739530683456"


def test_get_slides_url(parser, lecture_url):

    slides_url = parser.get_slides_url(lecture_url)

    assert slides_url.startswith("https://bbb.ssau.ru:8443/presentation/")
    assert slides_url.endswith("svgs/slide")


def test_download_slides(parser, lecture_url):

    slides_path = parser.download_slides(lecture_url)

    assert slides_path.exists()
    assert any(slides_path.iterdir())


def test_download_audio(parser, lecture_url):

    audio_path = parser.download_audio(lecture_url)

    length = parser.get_length(str(audio_path))

    print(f"Длина видео: {length} секунд")

    assert audio_path.exists()
    assert audio_path.name == "lecture.mp3"

    assert isinstance(length, float)
    assert length > 0


def test_get_metadata(parser):

    url = "https://bbb.ssau.ru/b/zat-vdd-mdu"

    metadata = parser.get_room_metadata(url)

    print(f"Metadata for {url}: \n{metadata}")

    assert isinstance(metadata, dict)
    assert len(metadata) > 0


def test_get_metadata_multiple(parser):

    expected_counts = {
        "https://bbb.ssau.ru/b/zat-vdd-mdu": 1,
        "https://bbb.ssau.ru/b/wgd-w68-zyv-lwn": 0,
        "https://bbb.ssau.ru/b/arc-gu6-rcm": 25
    }

    for url, expected_count in expected_counts.items():

        metadata = parser.get_room_metadata(url)

        actual_count = len(metadata)

        assert expected_count <= actual_count, (
            f"Для URL {url} ожидалось ≥ {expected_count}, получено {actual_count}"
        )

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
            headers=[
                "#",
                "Subject",
                "Teacher",
                "Datetime",
                "URL",
                "Length",
                "Users"
            ],
            tablefmt="github"
        ))
