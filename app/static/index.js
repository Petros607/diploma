const overlay = document.getElementById("overlay");

document.getElementById('searchButton').addEventListener('click', function() {
    const url = document.getElementById('urlInput');
    url_value = url.value;
    simulate_loading();
    if (url_value) {
        fetch(`/get_list?url_room=${encodeURIComponent(url_value)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка сервера');
                }
                return response.json();
            })
            .then(data => {
                overlay.style.display = "none";
                if (document.getElementById("tableSection").hasChildNodes()) {
                    modify_lections(data)
                } else {
                    set_lections(data);
                }
            })
            .catch(error => {
                overlay.style.display = "none";
                document.getElementById('response').innerText = 'Ссылка не найдена или произошла ошибка';
                console.error('Error:', error);
            }); 
    } else {
        document.getElementById('response').innerText = 'Пожалуйста, введите URL.';
    }
});

function set_lections(lections) {
    const parent_elem = document.getElementById("tableSection");
    for (let key in lections) {
        const lection = document.createElement("div");
        lection.className = "lections";
        let lection_url = lections[key]["url"];
        let buttonText = lections[key]['path'] == null ? 'Сгенерировать' : 'Скачать';
        
        lection.innerHTML = `
            <div class="lection_name_teacher">${lections[key]["name_teacher"]}</div>
            <div class="lection_title">${lections[key]["name_subject"]}</div>
            <div class="lection_time">${lections[key]["datetime"]}</div>
            <div class="lection_download_btn">
                <a href="#" onclick="downloadLecture('${lection_url}', event)" class="lecture_download_a">${buttonText}</a>
            </div>
        `;
        parent_elem.appendChild(lection);
    }
    parent_elem.classList.add("visible");
}

function modify_lections(lections) {
    const parent_elem = document.getElementById("tableSection");
    parent_elem.classList.remove("visible");
    parent_elem.innerHTML = "";
    set_lections(lections);
}

function simulate_loading() {
    overlay.style.display = "flex";
}

function downloadLecture(lection_url, event) {
    event.preventDefault();
    document.getElementById('response').innerText = '';
    simulate_loading();

    fetch(`/get_lecture?url_lecture=${encodeURIComponent(lection_url)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка загрузки');
            }
            return response.blob();
        })
        .then(blob => {
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            // link.download = 'conspect.pdf'; TODO
            link.download = 'conspect.txt';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(link.href);
            document.getElementById('response').innerText = 'Конспект успешно скачан!';
            document.getElementById('response').style.color = '#28a745';
            setTimeout(() => {
                document.getElementById('response').innerText = '';
            }, 3000);
        })
        .catch(error => {
            document.getElementById('response').innerText = 'Ошибка загрузки файла';
            console.error('Error:', error);
        })
        .finally(() => {
            overlay.style.display = "none";
        });
}

// Для тестирования можно использовать пример данных
const json = {
    "lection_0": {
        "id": null,
        "name_file": null,
        "name_teacher": "Грешняков Павел Иванович",
        "url": "https://bbb.ssau.ru:8443/playback/presentation/2.3/cf5215d4ed77ac8f39337081f34c2a49a413621d-1649044933105",
        "name_subject": "Робототехнические комплексы",
        "datetime": "Apr 04, 2022 4:02am",
        "lenght": null,
        "path": "что-то",
        "size": null
    },
    "lection_1": {
        "id": null,
        "name_file": null,
        "name_teacher": "Грешняков Павел Иванович",
        "url": "https://bbb.ssau.ru:8443/playback/presentation/2.3/cf5215d4ed77ac8f39337081f34c2a49a413621d-1645415216551",
        "name_subject": "Робототехнические комплексы",
        "datetime": "Feb 21, 2022 3:46am",
        "lenght": null,
        "path": null,
        "size": null
    },
    "lection_2": {
        "id": null,
        "name_file": null,
        "name_teacher": "Грешняков Павел Иванович",
        "url": "https://bbb.ssau.ru:8443/playback/presentation/2.3/cf5215d4ed77ac8f39337081f34c2a49a413621d-1636948468965",
        "name_subject": "Робототехнические комплексы",
        "datetime": "Nov 15, 2021 3:54am",
        "lenght": null,
        "path": null,
        "size": null
    }
};
