# tests/4_test_lecture_service.py

import asyncio
import pytest
from pathlib import Path
from fastapi.responses import FileResponse

from app.services.lecture_service import LectureService
from app.core.status import RequestStatus


class Dummy:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def lecture_service():
    return LectureService()


@pytest.fixture
def dummy_db():
    # we never actually use the db object in patched repository functions
    return object()


def test_get_status_with_existing_request(monkeypatch, lecture_service, dummy_db):
    lecture = Dummy(id=123)
    request = Dummy(status=RequestStatus.FINISHED)

    async def fake_get_lecture_by_url(db, url):
        return lecture

    async def fake_get_request_by_lecture_id(db, lid):
        assert lid == lecture.id
        return request

    monkeypatch.setattr(
        "app.repositories.lecture_repository.get_lecture_by_url",
        fake_get_lecture_by_url,
    )
    monkeypatch.setattr(
        "app.repositories.request_repository.get_request_by_lecture_id",
        fake_get_request_by_lecture_id,
    )

    loop = asyncio.new_event_loop()
    status = loop.run_until_complete(
        lecture_service.get_status("any", dummy_db)
    )
    loop.close()
    assert status == {"status": RequestStatus.FINISHED}


def test_get_status_when_lecture_missing(monkeypatch, lecture_service, dummy_db):
    async def fake_get_lecture_by_url(db, url):
        return None

    monkeypatch.setattr(
        "app.repositories.lecture_repository.get_lecture_by_url",
        fake_get_lecture_by_url,
    )

    loop = asyncio.new_event_loop()
    status = loop.run_until_complete(
        lecture_service.get_status("any", dummy_db)
    )
    loop.close()
    assert status == {"status": RequestStatus.PENDING}


def test_download_summary_success(tmp_path, monkeypatch, lecture_service, dummy_db):
    lecture = Dummy(id=555)
    # create temporary file to serve as pdf
    pdf_file = tmp_path / "lecture.pdf"
    pdf_file.write_text("dummy")

    summary = Dummy(summary_path=str(pdf_file))

    async def fake_get_lecture_by_url(db, url):
        return lecture

    async def fake_get_summary_by_lecture_id(db, lid):
        assert lid == lecture.id
        return summary

    monkeypatch.setattr(
        "app.repositories.lecture_repository.get_lecture_by_url",
        fake_get_lecture_by_url,
    )
    monkeypatch.setattr(
        "app.repositories.summary_repository.get_summary_by_lecture_id",
        fake_get_summary_by_lecture_id,
    )

    loop = asyncio.new_event_loop()
    response = loop.run_until_complete(
        lecture_service.download_summary("any", dummy_db)
    )
    loop.close()
    assert isinstance(response, FileResponse)
    # path property may be a Path object
    assert str(response.path) == str(pdf_file)


def test_download_summary_not_found(monkeypatch, lecture_service, dummy_db):
    async def fake_get_lecture_by_url(db, url):
        return None

    monkeypatch.setattr(
        "app.repositories.lecture_repository.get_lecture_by_url",
        fake_get_lecture_by_url,
    )

    with pytest.raises(FileNotFoundError):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(
            lecture_service.download_summary("any", dummy_db)
        )
        loop.close()
