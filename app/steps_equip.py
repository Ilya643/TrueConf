"""
Шаги конфигуратора: Двигатель, Опции, Цвет.

Продолжение пошагового конфигуратора:
Engine → Options → Color → InTotal.

Предыдущие шаги (модель, кузов, комплектация)
находятся в ``app.steps``.
"""

import os
import sqlite3

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QPainter, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton

import app.utils as state
from app.base_window import Window, _scale_pixmap
from app.utils import price_proc


def _parse_price(text_line: str) -> int:
    """Извлекает цену из строки кнопки вида «от 1 234 567 ₽».

    Args:
        text_line: Строка с ценой.

    Returns:
        Целочисленная цена в рублях.
    """
    return int(text_line.replace(" ", "").replace("от", "").rstrip("₽"))


class Engine(Window):
    """Окно выбора двигателя (шаг 4).

    Args:
        model: Название модели.
        body: Название кузова.
        equip: Название комплектации.
    """

    def __init__(self, model: str, body: str, equip: str) -> None:
        """Сохраняет параметры конфигурации."""
        self.mod, self.body, self.equip = model, body, equip
        super().__init__()
        self.initUI()

    def initUI(self) -> None:
        """Задаёт хлебные крошки и загружает двигатели."""
        super().initUI()
        self.pushButton.clicked.connect(self.main_window)
        crumbs = [
            (self.pushButton_2, f"01 {self.mod}"),
            (self.pushButton_3, f"02 {self.body}"),
            (self.pushButton_4, f"03 {self.equip}"),
            (self.pushButton_5, ""),
        ]
        for btn, text in crumbs:
            btn.setStyleSheet("background-color: #A92E18;")
            if text:
                btn.setText(text)
        self.pushButton_4.clicked.connect(self.back)
        self._load()

    def _load(self) -> None:
        """Читает двигатели из таблицы EQUIPMENT."""
        if not os.path.exists(state.db):
            self.db_error()
            return
        with sqlite3.connect(state.db) as con:
            result = con.execute(
                "SELECT * FROM EQUIPMENT WHERE Model=? AND Body=? "
                "AND Complectation=? AND Option='двигатель'",
                (self.mod, self.body, self.equip),
            ).fetchall()
        self.main(result, (4, 5, 6), "engine")
        self.label_2.setText("Двигатель Автомобиля")

    def show_window5(self) -> None:
        """Открывает шаг выбора опций с ценой выбранного двигателя."""
        button = QApplication.instance().sender()
        lines = button.text().split("\n")
        engine_price = _parse_price(lines[1])
        self._open(Options(self.mod, self.body, self.equip, [lines[0]], [engine_price]))

    def back(self) -> None:
        """Возвращается к выбору комплектации."""
        from app.steps import Complectation
        self._open(Complectation(self.mod, self.body))


class Options(Window):
    """Окно выбора дополнительных опций (шаг 5).

    Поддерживает toggle-выбор: повторный клик снимает опцию.

    Args:
        model: Название модели.
        body: Название кузова.
        equip: Название комплектации.
        characteristic: Список уже выбранных характеристик.
        price: Список цен выбранных характеристик.
    """

    def __init__(self, model: str, body: str, equip: str,
                 characteristic: list, price: list) -> None:
        """Инициализирует окно с данными конфигурации."""
        self.mod, self.body, self.equip = model, body, equip
        self.characteristic = characteristic
        self.price = price
        self.pixmaps: dict = {}   # {кнопка: [путь_фото, QLabel]}
        self.count: dict = {}     # {кнопка: количество_кликов}
        super().__init__()
        self.initUI()

    def initUI(self) -> None:
        """Задаёт хлебные крошки, кнопку «Далее» и загружает опции."""
        super().initUI()
        self.pushButton.clicked.connect(self.main_window)
        crumbs = [
            (self.pushButton_2, f"01 {self.mod}"),
            (self.pushButton_3, f"02 {self.body}"),
            (self.pushButton_4, f"03 {self.equip}"),
            (self.pushButton_5, ""),
            (self.pushButton_6, ""),
        ]
        for btn, text in crumbs:
            btn.setStyleSheet("background-color: #A92E18;")
            if text:
                btn.setText(text)
        self.pushButton_5.clicked.connect(self.back)
        self._load()

    def _load(self) -> None:
        """Читает доп. опции из таблицы EQUIPMENT и добавляет кнопку «Далее»."""
        if not os.path.exists(state.db):
            self.db_error()
            return
        with sqlite3.connect(state.db) as con:
            result = con.execute(
                "SELECT * FROM EQUIPMENT WHERE Model=? AND Body=? "
                "AND Complectation=? AND Option!='двигатель'",
                (self.mod, self.body, self.equip),
            ).fetchall()
        self.label_2.setText("Дополнительные Опции")
        if result:
            self.main(result, (3, 5, 6), "options")
        else:
            msg = QLabel("ДОПОЛНИТЕЛЬНЫХ ОПЦИЙ ДЛЯ ДАННОГО АВТОМОБИЛЯ НЕ ПРЕДУСМОТРЕНО", self)
            msg.setFont(QFont("Arial", 20))
            msg.setAlignment(Qt.AlignCenter)
            self.scroll.setWidget(msg)
            self.label.setText(state.brand)
            self.showMaximized()

        next_btn = QPushButton("Далее ❯", self)
        next_btn.setMinimumSize(200, 50)
        next_btn.setFont(QFont("Arial", 17))
        next_btn.clicked.connect(self._show_color)
        self.horizontalLayout.addWidget(next_btn)

    def _show_color(self) -> None:
        """Собирает выбранные опции и открывает шаг выбора цвета."""
        for btn, click_count in self.count.items():
            if click_count % 2 != 0:   # Нечётное число кликов = выбрано
                name_line, price_line = btn.text().split("\n")
                self.characteristic.append(name_line)
                self.price.append(_parse_price(price_line))
        self._open(Color(self.mod, self.body, self.equip, self.characteristic, self.price))

    def choice(self) -> None:
        """Переключает состояние опции и обновляет изображение (toggle)."""
        button = QApplication.instance().sender()
        self.count[button] = self.count.get(button, 0) + 1
        img_path, img_label = self.pixmaps[button]
        pixmap = _scale_pixmap(QPixmap(os.path.normpath(img_path)))
        if self.count[button] % 2 != 0:
            # Рисуем галочку поверх изображения при выборе опции
            painter = QPainter(pixmap)
            font = QFont()
            font.setPointSize(16)
            painter.setFont(font)
            painter.drawText(QPoint(20, 36), "✅")
            painter.end()
        img_label.setPixmap(pixmap)

    def back(self) -> None:
        """Возвращается к выбору двигателя."""
        self._open(Engine(self.mod, self.body, self.equip))


class Color(Window):
    """Окно выбора цвета кузова (шаг 6).

    Args:
        model: Название модели.
        body: Название кузова.
        equip: Название комплектации.
        characteristic: Список выбранных характеристик.
        price: Список цен выбранных характеристик.
    """

    def __init__(self, model: str, body: str, equip: str,
                 characteristic: list, price: list) -> None:
        """Инициализирует окно с данными конфигурации."""
        self.mod, self.body, self.equip = model, body, equip
        self.characteristic = characteristic
        self.price = price
        self.image: dict = {}   # {кнопка: путь_к_изображению_цвета}
        super().__init__()
        self.initUI()

    def initUI(self) -> None:
        """Задаёт хлебные крошки и загружает цвета."""
        super().initUI()
        self.pushButton.clicked.connect(self.main_window)
        crumbs = [
            (self.pushButton_2, f"01 {self.mod}"),
            (self.pushButton_3, f"02 {self.body}"),
            (self.pushButton_4, f"03 {self.equip}"),
            (self.pushButton_5, ""),
            (self.pushButton_6, ""),
            (self.pushButton_7, ""),
        ]
        for btn, text in crumbs:
            btn.setStyleSheet("background-color: #A92E18;")
            if text:
                btn.setText(text)
        self.pushButton_6.clicked.connect(self.back)
        self._load()

    def _load(self) -> None:
        """Читает доступные цвета из таблицы COLOR."""
        if not os.path.exists(state.db):
            self.db_error()
            return
        with sqlite3.connect(state.db) as con:
            result = con.execute(
                "SELECT * FROM COLOR WHERE Model=? AND Body=? AND Complectation=?",
                (self.mod, self.body, self.equip),
            ).fetchall()
        self.main(result, (3, 4, 5), "color")
        self.label_2.setText("Цвет Автомобиля")

    def show_window7(self) -> None:
        """Открывает итоговое окно с выбранным цветом."""
        button = QApplication.instance().sender()
        lines = button.text().split("\n")
        color_name = "".join(lines[:-1])
        color_price = _parse_price(lines[-1])
        self.characteristic.append(color_name)
        self.price.append(color_price)
        from app.summary import InTotal
        self._open(InTotal(self.mod, self.body, self.equip,
                           self.price, self.characteristic, self.image[button]))

    def back(self) -> None:
        """Возвращается к выбору опций."""
        self._open(Options(self.mod, self.body, self.equip,
                           self.characteristic, self.price))
