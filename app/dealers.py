"""
Карта дилеров LADA на базе Яндекс.Карт.

Модуль содержит единственный класс ``DealersMap``, который
отображает встроенную веб-карту с автоматическим поиском
официальных дилеров LADA в заданном городе.
"""

from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtWebEngineWidgets import QWebEngineView

import os
from dotenv import load_dotenv


# Ключ API Яндекс.Карт (ограниченный, только для разработки)
load_dotenv()
_YANDEX_API_KEY = os.getenv('YA_API_KEY')

# HTML-шаблон карты с плейсхолдерами {city} и {api_key}
_MAP_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://api-maps.yandex.ru/2.1/?apikey={api_key}&lang=ru_RU"></script>
    <style>
        html, body, #map {{ width: 100%; height: 100%; margin: 0; padding: 0; }}
        .status {{
            position: absolute; top: 10px; left: 50%;
            transform: translateX(-50%);
            background: #fff; padding: 8px 16px; border-radius: 20px;
            font-family: Arial, sans-serif; font-size: 13px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15); z-index: 1000;
            white-space: nowrap;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="status" id="status">
        🔍 Поиск дилеров LADA в г. {city}...
    </div>
    <script>
        ymaps.ready(init);
        function init() {{
            var map = new ymaps.Map("map", {{
                center: [55.751244, 37.618423],
                zoom: 10,
                controls: []
            }});

            var searchControl = new ymaps.control.SearchControl({{
                provider: 'yandex#search',
                results: 15,
                noCentering: true,
                noPlacemark: false
            }});

            searchControl.events.add('resultschange', function () {{
                var count = searchControl.getLength();
                var statusEl = document.getElementById('status');
                if (count > 0) {{
                    statusEl.textContent =
                        '✅ Найдено: ' + count + ' дилеров LADA';
                    map.setBounds(
                        searchControl.getResults().getBounds(),
                        {{ checkZoomRange: true, zoomMargin: 40 }}
                    );
                }} else {{
                    statusEl.textContent =
                        '❌ Дилеры не найдены. Проверьте название города.';
                }}
            }});

            searchControl.search('автосалон LADA {city}');
            map.controls.add(searchControl);

            // Скрываем поле ввода встроенного поиска Яндекс.Карт —
            // пользователь вводит город в наш собственный виджет выше
            setTimeout(function() {{
                var input = document.querySelector(
                    '.ymaps-2-1-79-search-control__input'
                );
                if (input) input.style.display = 'none';
            }}, 500);
        }}
    </script>
</body>
</html>
"""


class DealersMap(QWidget):
    """Окно карты официальных дилеров LADA.

    Позволяет пользователю:
    * ввести название города в строку поиска;
    * нажать «Найти» или клавишу Enter;
    * увидеть отмеченные на карте дилерские центры.

    По умолчанию ищет дилеров в Москве.

    Args:
        city: Город для первоначального поиска (по умолчанию «Москва»).
    """

    def __init__(self, city: str = "Москва") -> None:
        """Инициализирует виджет и запускает поиск для города по умолчанию."""
        super().__init__()
        self.showMaximized()
        self.city = city
        self._init_ui()

    def _init_ui(self) -> None:
        """Строит интерфейс: строка поиска + веб-карта."""
        self.setWindowTitle("Карта дилеров LADA")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # --- Строка поиска города ---
        search_row = QHBoxLayout()
        search_row.setSpacing(8)

        self.city_input = QLineEdit(self)
        self.city_input.setText(self.city)
        self.city_input.setPlaceholderText("Введите город...")
        self.city_input.setMaximumHeight(32)
        # Enter в поле сразу запускает поиск
        self.city_input.returnPressed.connect(self._search)
        search_row.addWidget(self.city_input, 1)

        find_btn = QPushButton("🔍 Найти", self)
        find_btn.setMaximumHeight(32)
        find_btn.clicked.connect(self._search)
        search_row.addWidget(find_btn)

        layout.addLayout(search_row)

        # --- Встроенная карта ---
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view, 1)

        # Загружаем карту с начальным городом
        self._load_map(self.city)
        self.show()

    def _search(self) -> None:
        """Читает город из поля ввода и перезагружает карту."""
        city = self.city_input.text().strip()
        if city:
            self.city = city
            self._load_map(city)

    def _load_map(self, city: str) -> None:
        """Генерирует HTML с картой и загружает его в WebEngineView.

        Args:
            city: Название города для поиска дилеров.
        """
        # Экранируем кавычки, чтобы не сломать JS-строки
        safe_city = city.replace("'", "\\'").replace('"', '\\"')
        html = _MAP_HTML_TEMPLATE.format(
            api_key=_YANDEX_API_KEY,
            city=safe_city,
        )
        self.web_view.setHtml(html)
