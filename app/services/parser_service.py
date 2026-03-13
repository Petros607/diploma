# app/services/parser_service.py
"""Сервис для парсинга и загрузки лекций с BigBlueButton."""

import pathlib
import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pytz
import av

class ParserService:
    BASE_URL = "https://bbb.ssau.ru:8443"
    SAMARA_TZ = pytz.timezone("Europe/Samara")
    PATH_FILES = pathlib.Path("data/")

    def __init__(self) -> None:
        """Инициализирует сессию для HTTP-запросов."""
        self.session: requests.Session = requests.Session()

    def _extract_recording_id(self, lecture_url: str) -> str:
        """Извлекает ID записи из URL лекции BigBlueButton.
        Args:
            lecture_url: URL лекции в формате 
                https://bbb.../playback/presentation/2.3/<recording_id>
        Returns:
            ID записи, извлечённый из URL.
        """
        return lecture_url.rstrip("/").split("/")[-1]
    
    def _convert_time(self, iso_datetime: str, fallback: str) -> str:
        """Преобразует время из UTC в часовой пояс Самары.
        
        Args:
            iso_datetime: Время в формате ISO (UTC).
            fallback: Значение по умолчанию в случае ошибки.
        
        Returns:
            Отформатированная строка с временем в самарском часовом поясе.
        """
        try:
            utc_time = datetime.fromisoformat(iso_datetime.replace("Z", "+00:00"))
            utc_time = utc_time.replace(tzinfo=pytz.UTC)
            samara_time = utc_time.astimezone(self.SAMARA_TZ)
            formatted = samara_time.strftime("%b %d, %Y %I:%M%p")
            return formatted.replace("AM", "am").replace("PM", "pm")
        except Exception:
            return fallback
    
    async def download_audio(self, lecture_url: str, lecture_id: int) -> pathlib.Path:
        """Скачивает аудио/видео лекции и конвертирует в MP3.
        Args:
            lecture_url: URL лекции на BigBlueButton.
            lecture_id: ID лекции.
        Returns:
            mp3_path: Путь к сохранённому аудиофайлу.
        Raises:
            requests.HTTPError: Если при скачивании произошла ошибка.
        """
        recording_id = self._extract_recording_id(lecture_url)
        audio_url = (
            f"{self.BASE_URL}/presentation/{recording_id}/video/webcams.webm"
        )
        save_dir = self.PATH_FILES / str(lecture_id)
        os.makedirs(save_dir, exist_ok=True)
        mp3_path = save_dir / "audio.mp3"

        response = self.session.get(audio_url, stream=True)
        response.raise_for_status()

        container = av.open(response.raw)
        audio_stream = next(s for s in container.streams if s.type == "audio")

        output = av.open(str(mp3_path), "w")
        out_stream = output.add_stream(
            codec_name="mp3", rate=audio_stream.rate, 
            layout='mono', bit_rate = 64000, format = 's16p'
        )
        for frame in container.decode(audio_stream):
            packet = out_stream.encode(frame)
            if packet:
                output.mux(packet)
        packet = out_stream.encode(None)
        if packet:
            output.mux(packet)
        output.close()
        container.close()
        return mp3_path

    def get_length(self, path: str | pathlib.Path) -> float:
        """Получает длительность медиафайла в секундах.
        Args:
            path: Путь к медиафайлу.
        Returns:
            Длительность файла в секундах.
        """
        container = av.open(str(path))
        stream = next(s for s in container.streams if s.type == "audio")
        duration = float(stream.duration * stream.time_base)
        container.close()
        return duration
    
    def get_slides_url(self, lecture_url: str) -> str:
        """Извлечение базовый URL для скачивания слайдов лекции.
        Args:
            lecture_url: URL лекции на BigBlueButton.
        Returns:
            Базовый URL для скачивания слайдов (без номера слайда).
        """
        recording_id = self._extract_recording_id(lecture_url) #097c80a16ee9277077ca6a347f6e8f9c597b9a62-1759998690614
        json_url = f"{self.BASE_URL}/presentation/{recording_id}/presentation_text.json" # "https://bbb.ssau.ru:8443/presentation/097c80a16ee9277077ca6a347f6e8f9c597b9a62-1759998690614/presentation_text.json"
        response = self.session.get(json_url)
        content = response.json()
        presentation_id = list(content.keys())[1]
        slides_base = (
            f"{self.BASE_URL}/presentation/"
            f"{recording_id}/presentation/"
            f"{presentation_id}/svgs/slide" #2648fa4acbe79cc0a2bbae0297d12d35e139aa64-1759998714887
        )
        return slides_base
    
    async def download_slides(self, lecture_url: str, lecture_id: int) -> pathlib.Path:
        """Скачивает все слайды лекции.
        Args:
            lecture_url: URL лекции на BigBlueButton.
            lecture_id: ID лекции.
        Returns:
            save_dir: Путь к директории с сохранёнными слайдами.
        """
        slides_base = self.get_slides_url(lecture_url)
        save_dir = self.PATH_FILES / str(lecture_id) / "presentation"
        os.makedirs(save_dir, exist_ok=True)
        i = 1
        while True:
            slide_url = f"{slides_base}{i}.svg"
            response = self.session.get(slide_url)
            if response.status_code != 200:
                break
            slide_number = f"{i:04d}"
            file_path = save_dir / f"slide{slide_number}.svg"
            with open(file_path, "wb") as f:
                f.write(response.content)
            i += 1
        return save_dir

    def _parse_page(
        self, 
        soup: BeautifulSoup, 
        teacher_name: str, 
        subject_title: str, 
        data: dict[str, dict],
        index: int
    ) -> dict[str, dict]:
        """Парсит страницу с записями лекций.
        Args:
            soup: Объект BeautifulSoup с HTML страницы.
            teacher_name: Имя преподавателя.
            subject_title: Название предмета.
            data: Словарь для накопления результатов.
            start_index: Начальный индекс для добавления записей.
        Returns:
            Обновлённый словарь с данными лекций.
        """
        table = soup.find("table", id="recordings-table")
        if not table:
            return data
        for row in table.find_all("tr"):
            time_tag = row.find("time")
            link_tag = row.find("a", class_="btn btn-sm btn-primary")
            if not time_tag or not link_tag:
                continue
            datetime_utc = time_tag["datetime"]
            lecture_url = link_tag["href"]
            length_tag = row.find("td", id="recording-length")
            users_tag = row.find("td", id="recording-users")
            length = length_tag.get_text(strip=True) if length_tag else None
            users_text = users_tag.get_text(strip=True) if users_tag else None
            users_count = int(users_text) if users_text and users_text.isdigit() else None
            datetime_local = self._convert_time(
                datetime_utc,
                time_tag.get_text(strip=True)
            )
            data[f"lecture_{index}"] = {
                "name_teacher": teacher_name,
                "url": lecture_url,
                "name_subject": subject_title,
                "datetime": datetime_local,
                "datetime_utc": datetime_utc,
                "length": length,
                "users_count": users_count
            }
            index += 1
        return data

    def get_room_metadata(self, url: str) -> dict[str, dict]:
        """Парсит комнату предмета и получает метаданные всех лекций.
        Args:
            url: URL комнаты предмета на BigBlueButton.
        Returns:
            Словарь с метаданными лекций, где ключи - 'lecture_0', 'lecture_1' и т.д.
        Raises:
            requests.RequestException: Если при запросе произошла ошибка.
            AttributeError: Если не удалось найти необходимые элементы на странице.
        """
        data = {}
        base_url = url.split("?")[0]
        response = requests.get(base_url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        subject_title = soup.find("h1", class_="display-3 text-left mb-3 font-weight-400")
        if subject_title: subject_title = subject_title.get_text(strip=True) or "Без названия"
        teacher_name = soup.find("h5", id="room-owner-name")
        if teacher_name: teacher_name = teacher_name.get_text(strip=True).replace(" (Владелец)", "").replace("(Owner) ", "").strip() or "Без имени"
        pages = []
        nav = soup.find("nav", class_="pagy-bootstrap-nav")
        if nav:
            for link in nav.find_all("a")[1:-1]:
                href = link.get("href")
                if href and "page=" in href:
                    pages.append(urljoin(url, href))
        index = 0

        for page in pages:
            response = requests.get(page, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            data = self._parse_page(
                soup,
                teacher_name,
                subject_title,
                data,
                index
            )
            index = len(data)
        return data
