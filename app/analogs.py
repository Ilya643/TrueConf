"""
Поиск аналогов на Auto.ru.

Содержит класс ``AnalogSearch`` - встроенный браузер с автоматически
построенным URL-ом поиска похожих автомобилей на Auto.ru.

Фильтры поиска:
* модель и тип кузова;
* ценовой диапазон ±30 %;
* объём двигателя ±10 %.
"""

import re
import webbrowser

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)
from PyQt5.QtWebEngineWidgets import QWebEngineProfile, QWebEngineView

from app.utils import price_proc


class AnalogSearch(QWidget):
    """Встроенный браузер для поиска аналогов на Auto.ru.

    Автоматически строит URL с фильтрами по модели, кузову,
    ценовому диапазону и объёму двигателя.

    Args:
        model: Название модели LADA (например, «Granta»).
        body: Тип кузова (например, «седан»).
        prices: Список цен конфигурации; первый элемент - базовая цена.
        characteristics: Список характеристик; первый - двигатель.
    """

    # Соответствие русских типов кузова URL-slug'ам Auto.ru
    _BODY_MAP: dict = {
        "седан": "sedan", "хэтчбек": "hatchback",
        "универсал": "universal", "внедорожник": "suv",
        "джип": "suv", "кроссовер": "crossover", "лифтбек": "liftback",
    }

    # Соответствие названий моделей URL-путям Auto.ru
    _MODEL_MAP: dict = {
        "granta": "granta/", "vesta": "vesta/", "largus": "largus/",
        "niva": "niva/", "xray": "xray/", "priora": "priora/", "aura": "aura/",
    }

    def __init__(self, model: str, body: str, prices: list,
                 characteristics: list) -> None:
        """Строит URL и открывает браузерное окно."""
        super().__init__()
        self.model = model
        self.body = body
        self.base_price = prices[0] if prices else 0
        self.characteristics = characteristics

        # Настраиваем User-Agent чтобы Auto.ru воспринимал запрос как браузерный
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        profile.setHttpAcceptLanguage("ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7")

        self.url = self._build_url()
        try:
            self._init_ui()
            self._load()
        except Exception:
            # Запасной вариант: открываем в системном браузере
            webbrowser.open(self.url)
            self.close()

    def _init_ui(self) -> None:
        """Строит интерфейс: панель инструментов + встроенный браузер."""
        self.setWindowTitle("🔍 Поиск аналогов на Auto.ru")
        self.showMaximized()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Верхняя панель с информацией
        top = QHBoxLayout()
        info = QLabel(f"🚗 {self.model} {self.body} • от {price_proc(self.base_price)} ₽")
        info.setFont(QFont("Arial", 12))
        top.addWidget(info)
        top.addStretch()

        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(lambda: self.browser.reload())
        top.addWidget(refresh_btn)

        open_btn = QPushButton("🌐 Открыть в браузере")
        open_btn.clicked.connect(lambda: webbrowser.open(self.url))
        top.addWidget(open_btn)

        layout.addLayout(top)

        # Встроенный браузер PyQT
        self.browser = QWebEngineView()
        layout.addWidget(self.browser, 1)

        # Строка состояния
        self.status = QLabel("Загрузка...")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("background: #f0f0f0; padding: 4px; color: #555;")
        layout.addWidget(self.status)

        self.show()

    def _load(self) -> None:
        """Загружает URL в браузер и подключает обработчик завершения."""
        self.status.setText("Загрузка Auto.ru...")
        self.browser.load(QUrl(self.url))
        self.browser.loadFinished.connect(self._on_loaded)

    def _on_loaded(self, ok: bool) -> None:
        """Обновляет статусную строку после загрузки страницы.

        Args:
            ok: True если страница загружена успешно.
        """
        if ok:
            self.status.setText("✅ Auto.ru загружен")
        else:
            self.status.setText('❌ Ошибка загрузки! Нажмите "Открыть в браузере".')

    def _build_url(self) -> str:
        """Формирует URL поиска на Auto.ru с нужными фильтрами.

        Returns:
            Готовый URL строки для Auto.ru.
        """
        base = "https://auto.ru/cars/vaz/"
        model_path = next(
            (v for k, v in self._MODEL_MAP.items() if k in self.model.lower()), None
        )
        if not model_path:
            return "https://auto.ru/cars/vaz/used/"
        base += model_path + "used/"

        body_slug = next(
            (v for k, v in self._BODY_MAP.items() if k in self.body.lower()), None
        )
        if body_slug:
            base += f"body-{body_slug}/"

        params = [
            f"price_from={int(self.base_price * 0.7)}",
            f"price_to={int(self.base_price * 1.3)}",
        ]

        # Ищем объём двигателя в строке вида «1.6 л (90 л.с.)»
        for char in self.characteristics:
            match = re.search(r"(\d+\.?\d*)\s*л", char)
            if match:
                disp = float(match.group(1))
                delta = max(0.1, disp * 0.1)
                params += [
                    f"displacement_from={round(disp - delta, 1)}",
                    f"displacement_to={round(disp + delta, 1)}",
                ]
                break

        params.append("sort=cr_date-desc")
        return base + "?" + "&".join(params)
