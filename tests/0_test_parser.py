import pytest
from app.services.parser_service import ParserService

TEST_URL = "https://bbb.ssau.ru:8443/playback/presentation/2.3/aa788c4e3599195fe1a7a12ad585903f44c6f9ed-1739185560849"

@pytest.mark.asyncio
def test_get_data():
    parser = ParserService()
    slides_url = parser.get_data(TEST_URL)
    assert slides_url.startswith("https://bbb.ssau.ru:8443/presentation/"), "Неверная ссылка на слайды"
