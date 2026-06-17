"""
Главное меню приложения и окно настроек.

Модуль содержит классы:

* ``MainWindow`` — стартовый экран с кнопками «Конфигуратор»,
  «Настройки», «Выход» и выбором бренда.
* ``Settings``   — окно обновления базы данных с настройками прокси.
* ``Load``       — заглушка «Ожидайте загрузки...».
"""

import time

from PyQt5 import uic, QtGui
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QWidget
import webbrowser

import DBUPDATE
import app.utils as state


# Главное меню
class MainWindow(QWidget):
    """Главное меню конфигуратора LADA.

    Отображает фоновое изображение автомобиля и три управляющих кнопки:
    «Конфигуратор», «Настройки», «Выход».  Также содержит ComboBox
    для выбора бренда/базы данных.
    """

    def __init__(self) -> None:
        """Инициализирует главное окно и загружает UI из ``mainmm.ui``."""
        super().__init__()
        uic.loadUi("./ui/mainmm.ui", self)
        self.showFullScreen()
        self._init_ui()

    def _init_ui(self) -> None:
        """Настраивает заголовок, подключает сигналы кнопок и заполняет ComboBox."""
        self.setWindowTitle("Конфигуратор LADA")

        # Кнопка «Конфигуратор» — начало процесса выбора
        self.pushButton.clicked.connect(self._show_configurator)

        # Кнопка «Выход» — завершает приложение
        self.pushButton_2.clicked.connect(self.close)

        # Кнопка «Настройки» — открывает окно обновления БД
        self.pushButton_3.clicked.connect(self._show_settings)

        # Кнопка разработчика — открывает Telegram
        self.pushButton_4.clicked.connect(
            lambda: webbrowser.open("https://t.me/Lil_soupchik")
        )

        # Заполняем выпадающий список доступными брендами из DBUPDATE
        for brand_name, db_file in DBUPDATE.brands.items():
            self.comboBox.addItem(brand_name, db_file)

    def _show_configurator(self) -> None:
        """Сохраняет выбранный бренд и открывает окно выбора модели."""
        # Обновляем глобальное состояние сессии
        state.set_session(
            db_path=self.comboBox.currentData(),
            brand_name=self.comboBox.currentText(),
        )
        # Отложенный импорт для избежания циклических зависимостей
        from app.steps import Model
        self.w = Model()
        self.w.show()
        self.hide()

    def _show_settings(self) -> None:
        """Открывает окно настроек и обновления базы данных."""
        self.w = Settings()
        self.w.show()
        self.hide()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        """Рисует фоновое изображение автомобиля на всю площадь окна.

        Args:
            event: Событие перерисовки Qt.
        """
        painter = QPainter(self)
        pixmap = QPixmap(
            "./36731-predstavitelskij_avtomobil-koleso-audi-sportkar-doroga-1920x1080.jpg"
        )
        painter.drawPixmap(self.rect(), pixmap)


# Настройки
class Settings(QWidget):
    """Окно настроек приложения.

    Позволяет обновить базу данных с сайта LADA и настроить
    параметры прокси (checkBox) и заголовков (checkBox_2).
    Обновление доступно не чаще одного раза в 30 минут (cooldown).
    """

    def __init__(self) -> None:
        """Инициализирует окно настроек и загружает ``settings.ui``."""
        super().__init__()
        uic.loadUi("./ui/settings.ui", self)
        self._init_ui()

    def _init_ui(self) -> None:
        """Фиксирует размер окна, подключает кнопки."""
        self.setFixedSize(700, 500)
        self.setWindowTitle("Настройки")

        # Кнопка «Обновить БД»
        self.pushButton_3.clicked.connect(self._update_db)

        # Кнопка «Назад» — возврат в главное меню
        self.pushButton_4.clicked.connect(self._back)

    def _update_db(self) -> None:
        """Запускает обновление БД при соблюдении cooldown 30 минут.

        Если с момента последнего обновления прошло менее 30 минут,
        вызов игнорируется.  После успешного обновления сохраняет
        текущее время в ``state.timeup``.
        """
        # Cooldown: 1800 секунд = 30 минут
        if time.monotonic() - state.timeup <= 1800:
            return

        load_window = Load()
        load_window.show()
        self.hide()

        # Передаём настройки прокси и заголовков из чекбоксов
        DBUPDATE.all_update(
            proxy=self.checkBox.isChecked(),
            use_headers=self.checkBox_2.isChecked(),
        )

        # Фиксируем время обновления для cooldown
        state.timeup = time.monotonic()

        load_window.close()
        self.show()

    def _back(self) -> None:
        """Возвращает пользователя в главное меню."""
        self.w = MainWindow()
        self.w.show()
        self.hide()


# Окно ожидания
class Load(QWidget):
    """Модальная заглушка «Ожидайте окончания загрузки».

    Отображается во время долгой операции обновления базы данных,
    чтобы пользователь понимал, что приложение работает.
    """

    def __init__(self) -> None:
        """Загружает UI и задаёт минимальный фиксированный размер."""
        super().__init__()
        uic.loadUi("./ui/load.ui", self)
        self.setWindowTitle("Ожидайте окончания загрузки")
        # Минимальная высота — окно служит лишь индикатором
        self.setFixedSize(400, 1)
