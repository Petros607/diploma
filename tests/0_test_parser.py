# tests/0_test_parser.py
from app.services.parser_service import ParserService
from tabulate import tabulate


# @pytest.mark.asyncio
def test_parser_download_lecture():
    # https://bbb.ssau.ru/b/zat-vdd-mdu
    TEST_URL = "https://bbb.ssau.ru:8443/playback/presentation/2.3/097c80a16ee9277077ca6a347f6e8f9c597b9a62-1772091088848"
    parser = ParserService()
    
    # Получаем URL слайда
    slides_url = parser.get_data(TEST_URL)
    assert slides_url.startswith("https://bbb.ssau.ru:8443/presentation/")
    
    # Скачиваем слайды
    slides_path = parser.download_image(slides_url)
    assert slides_path.exists() and any(slides_path.iterdir()), "Слайды не скачались"
    
    # Скачиваем аудио
    audio_path = parser.download_audio(slides_url)
    assert audio_path.exists(), "Аудио не скачалось"
    
    # Получаем длительность аудио
    length = parser.get_length(str(audio_path))
    assert length > 0, "Неверная длительность аудио"

def test_parser_get_metadata():

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
