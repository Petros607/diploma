const overlay = document.getElementById("overlay");

document.getElementById('searchButton').addEventListener('click', function() {
    const urlInput = document.getElementById('urlInput');
    const url_value = urlInput.value.trim();

    if (!url_value) {
        document.getElementById('response').innerText = 'Пожалуйста, введите URL.';
        return;
    }

    if (!url_value.startsWith('https://bbb.ssau.ru/b/')) {
        document.getElementById('response').innerText = 'Пожалуйста, введите корректную ссылку на комнату BBB (начинается с https://bbb.ssau.ru/b/)';
        return;
    }

    simulate_loading();

    if (url_value) {
        fetch(`/lectures/list?url_room=${encodeURIComponent(url_value)}`)
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
                document.getElementById('response').innerText = '';
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
        let status = lections[key]['status'];
        let buttonConfig = getButtonConfig(lection_url, status);

        lection.innerHTML = `
            <div class="lection_name_teacher">${lections[key]["name_teacher"]}</div>
            <div class="lection_title">${lections[key]["name_subject"]}</div>
            <div class="lection_time">${lections[key]["datetime"]}</div>
            <div class="lection_length">${lections[key]["length"]}</div>
            <div class="lection_users_count">${lections[key]["users_count"]} users</div>
            <div class="lection_download_btn">
                <a href="#"
                    onclick="${buttonConfig.onClick}"
                    class="lecture_download_a ${buttonConfig.className}"
                    style="${buttonConfig.style}">
                    ${buttonConfig.text}
                </a>
            </div>
        `;
        parent_elem.appendChild(lection);
    }
    parent_elem.classList.add("visible");
}

function getButtonConfig(lection_url, status) {
    let config = {
        text: "Сгенерировать",
        onClick: `handleGenerate('${lection_url}', event)`,
        className: "generate-btn",
        style: ""
    };
    
    if (status === "download") {
        config.text = "Скачать";
        config.onClick = `handleDownload('${lection_url}', event)`;
        config.className = "download-btn";
    }
    
    if (status === "processing") {
        config.text = "Генерируется...";
        config.onClick = "return false;"; // Ничего не делает при клике
        config.className = "processing-btn";
        config.style = "pointer-events:none;opacity:0.6;";
    }
    
    return config;
}

function handleGenerate(lection_url, event) {
    event.preventDefault();
    
    const clickedElement = event.target;
    const parentDiv = clickedElement.closest('.lection_download_btn');
    
    if (parentDiv) {
        clickedElement.style.pointerEvents = "none";
        clickedElement.style.opacity = "0.6";
        clickedElement.textContent = "Генерируется...";
    }
    
    document.getElementById('response').innerText = '';
    simulate_loading();

    fetch(`/lectures/generate?url_lecture=${encodeURIComponent(lection_url)}`, {
        method: 'POST',
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка генерации');
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('response').innerText = 'Генерация конспекта началась!';
            document.getElementById('response').style.color = '#28a745';
            
            // Обновляем статус лекции через некоторое время
            setTimeout(() => checkLectureStatus(lection_url, clickedElement), 10000);
        })
        .catch(error => {
            document.getElementById('response').innerText = 'Ошибка при генерации';
            document.getElementById('response').style.color = '#dc3545';
            console.error('Error:', error);
            
            // Возвращаем кнопку в исходное состояние при ошибке
            if (parentDiv) {
                clickedElement.style.pointerEvents = "auto";
                clickedElement.style.opacity = "1";
                clickedElement.textContent = "Сгенерировать";
            }
        })
        .finally(() => {
            overlay.style.display = "none";
        });
}

function handleDownload(lection_url, event) {
    event.preventDefault();
    document.getElementById('response').innerText = '';
    simulate_loading();

    fetch(`/lectures/download?url_lecture=${encodeURIComponent(lection_url)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка загрузки');
            }
            
            // Проверяем тип контента
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                // Если пришёл JSON с ошибкой
                return response.json().then(data => {
                    throw new Error(data.error || 'Ошибка при скачивании');
                });
            }
            
            return response.blob();
        })
        .then(blob => {
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            // Можно определять расширение по типу файла, но пока оставим .txt
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
            document.getElementById('response').innerText = error.message || 'Ошибка загрузки файла';
            document.getElementById('response').style.color = '#dc3545';
            console.error('Error:', error);
        })
        .finally(() => {
            overlay.style.display = "none";
        });
}

function checkLectureStatus(lection_url, buttonElement) {
    fetch(`/lectures/status?url_lecture=${encodeURIComponent(lection_url)}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === "download") {
                buttonElement.style.pointerEvents = "auto";
                buttonElement.style.opacity = "1";
                buttonElement.textContent = "Скачать";
                buttonElement.onclick = function(e) {
                    handleDownload(lection_url, e);
                };
                buttonElement.classList.remove("generate-btn");
                buttonElement.classList.add("download-btn");
            } else if (data.status === "processing") {
                // Всё ещё генерируется, проверяем через 10 секунд
                setTimeout(() => checkLectureStatus(lection_url, buttonElement), 10000);
            }
        })
        .catch(error => {
            console.error('Error checking status:', error);
        });
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
