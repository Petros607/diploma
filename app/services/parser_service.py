# app/schemas/parser_service.py
import pathlib
import os
import urllib
import subprocess
import json
import requests
from bs4 import BeautifulSoup

PATH_files = pathlib.Path("data/temp")

class ParserService:

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

    def get_metadata(self, url: str):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        lection_title = soup.find('h1', class_="display-3 text-left mb-3 font-weight-400").get_text(strip=True)
        teacher_name = soup.find('h5', id="room-owner-name",
                                 class_="font-weight-normal ml-4 mt-3 d-inline-block").get_text(strip=True).replace(
            " (Владелец)", "")
        lections_table = soup.find_all("table", id="recordings-table")[0]
        lections = lections_table.find_all("tr")[2:]
        data = {}
        for i, lection in enumerate(lections):
            time = lection.find("time").get_text(strip=True)
            lection_url = lection.find("a", class_="btn btn-sm btn-primary", target="_blank").get_attribute_list("href")[0]
            data[f'lection_{i}'] = {
                "id": None,
                "name_file": None,
                "name_teacher": teacher_name,
                "url": lection_url,
                "name_subject": lection_title,
                "datetime": time,
                "length": None,
                "path": None,
                "size": None
            }
        return data

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
