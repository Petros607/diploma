# app/schemas/parser_service.py
import pathlib
import os
import urllib
import subprocess
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import pytz

PATH_files = pathlib.Path("data/temp")

class ParserService:

    SAMARA_TZ = pytz.timezone("Europe/Samara")

    def get_data(self, url: str):
        page = requests.get(
            url.replace("/playback", "").replace("/2.3", "") + "/presentation_text.json"
        )
        content = json.loads(page.content)
        string = ""
        for key in content.keys():
            string += key + " "
        return "https://bbb.ssau.ru:8443/presentation/" + url.split("/")[6] + "/presentation/" + string.split(" ")[1] + "/svgs/slide" + "&" + string.split(" ")[1]

    def download_audio(self, url: str):
        id = url.split("/")[4]
        audio_id = url.split("&")[0].split("/")[4]
        audio_url = f"https://bbb.ssau.ru:8443/presentation/{audio_id}/video/webcams.webm"

        path_id = PATH_files / id
        os.makedirs(path_id / "audio", exist_ok=True)

        urllib.request.urlretrieve(audio_url, path_id / "audio/lecture.webm")
        return path_id / "audio/lecture.webm"
    
    def get_length(self, path: str):
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        duration = result.stdout.decode('utf-8').strip()
        return float(duration)

    def download_image(self, url: str):
        i = 1
        url_base = url.split("&")[0]
        id_for_path = url.split("/")[4]
        path_id = PATH_files / id_for_path
        os.makedirs(path_id / 'slides', exist_ok=True)

        while True:
            save_path = path_id / f"slides/slide{i}.svg"
            response = requests.get(url_base + str(i) + ".svg")
            if response.status_code == 200:
                with open(save_path, "wb") as file:
                    file.write(response.content)
                i += 1
            else:
                break
        return path_id / 'slides'
    
    def _convert_time(self, iso_datetime: str, fallback: str) -> str:
        """Конвертирует UTC время в Самарское."""
        try:
            utc_time = datetime.fromisoformat(iso_datetime.replace("Z", "+00:00"))
            utc_time = utc_time.replace(tzinfo=pytz.UTC)

            samara_time = utc_time.astimezone(self.SAMARA_TZ)

            formatted = samara_time.strftime("%b %d, %Y %I:%M%p")
            return formatted.replace("AM", "am").replace("PM", "pm")

        except Exception:
            return fallback

    def _parse_page(self, soup, teacher_name, subject_title, data, index):
        """Парсит страницу с записями и добавляет данные в словарь."""
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

    def get_metadata(self, url: str):
        """Парсинг комнаты предмета и получение метаданных всех лекций."""
        data = {}

        base_url = url.split("?")[0]

        response = requests.get(base_url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        subject_title = soup.find(
            "h1",
            class_="display-3 text-left mb-3 font-weight-400"
        ).get_text(strip=True)

        teacher_name = soup.find(
            "h5",
            id="room-owner-name"
        ).get_text(strip=True).replace(" (Владелец)", "")

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
