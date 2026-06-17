"""
Шаги конфигуратора: Модель, Кузов, Комплектация.

Первые три шага выбора в пошаговом конфигураторе:
Model → Body → Complectation.

Следующие шаги (двигатель, опции, цвет) находятся в
``app.steps_equip``.
"""

import os
import sqlite3

from PyQt5.QtWidgets import QApplication

import app.utils as state
from app.base_window import Window


class Model(Window):
    """Окно выбора модели автомобиля (шаг 1).

    Загружает список моделей из таблицы MODEL и отображает карточки.
    При выборе открывает ``Body``.
    """

    def __init__(self) -> None:
        """Инициализирует шаг и отображает список моделей."""
        super().__init__()
        self.initUI()

    def initUI(self) -> None:
        """Подключает навигацию и загружает данные."""
        super().initUI()
        self.pushButton.clicked.connect(self.back)
        self.pushButton_2.setStyleSheet("background-color: #A92E18;")
        self._load()

    def _load(self) -> None:
        """Читает модели из БД и отображает карточки."""
        if not os.path.exists(state.db):
            self.db_error()
            return
        with sqlite3.connect(state.db) as con:
            result = con.execute("SELECT * FROM Model").fetchall()
        self.main(result, (0, 1, 2), "model")
        self.label_2.setText("Семейство и Модель")

    def show_window2(self) -> None:
        """Открывает шаг выбора кузова для выбранной модели."""
        button = QApplication.instance().sender()
        model_name = button.text().split("\n")[0].replace("Семейство ", "")
        self._open(Body(model_name))

    def back(self) -> None:
        """Возвращает пользователя в главное меню."""
        from app.main_window import MainWindow
        self._open(MainWindow())


class Body(Window):
    """Окно выбора типа кузова (шаг 2).

    Args:
        model: Название выбранной модели.
    """

    def __init__(self, model: str) -> None:
        """Сохраняет модель и инициализирует окно."""
        self.model = model
        super().__init__()
        self.initUI()

    def initUI(self) -> None:
        """Задаёт хлебные крошки и загружает кузова."""
        super().initUI()
        self.pushButton.clicked.connect(self.main_window)
        self.pushButton_2.setStyleSheet("background-color: #A92E18;")
        self.pushButton_2.setText(f"01 {self.model}")
        self.pushButton_2.clicked.connect(self.back)
        self.pushButton_3.setStyleSheet("background-color: #A92E18;")
        self._load()

    def _load(self) -> None:
        """Читает кузова для выбранной модели из БД."""
        if not os.path.exists(state.db):
            self.db_error()
            return
        with sqlite3.connect(state.db) as con:
            result = con.execute(
                "SELECT * FROM BODY WHERE Model = ?", (self.model,)
            ).fetchall()
        self.main(result, (1, 2, 3), "body")
        self.label_2.setText("Кузов Автомобиля")

    def show_window3(self) -> None:
        """Открывает шаг выбора комплектации."""
        button = QApplication.instance().sender()
        body_name = button.text().split("\n")[0]
        self._open(Complectation(self.model, body_name))

    def back(self) -> None:
        """Возвращается к выбору модели."""
        self._open(Model())


class Complectation(Window):
    """Окно выбора комплектации (шаг 3).

    Args:
        model: Название модели.
        body: Название кузова.
    """

    def __init__(self, model: str, body: str) -> None:
        """Сохраняет модель и кузов, инициализирует окно."""
        self.mod = model
        self.body = body
        super().__init__()
        self.initUI()

    def initUI(self) -> None:
        """Задаёт хлебные крошки и загружает комплектации."""
        super().initUI()
        self.pushButton.clicked.connect(self.main_window)
        self.pushButton_2.setStyleSheet("background-color: #A92E18;")
        self.pushButton_2.setText(f"01 {self.mod}")
        self.pushButton_3.setText(f"02 {self.body}")
        self.pushButton_3.setStyleSheet("background-color: #A92E18;")
        self.pushButton_3.clicked.connect(self.back)
        self.pushButton_4.setStyleSheet("background-color: #A92E18;")
        self._load()

    def _load(self) -> None:
        """Читает комплектации для выбранной модели и кузова."""
        if not os.path.exists(state.db):
            self.db_error()
            return
        with sqlite3.connect(state.db) as con:
            result = con.execute(
                "SELECT * FROM COMPLECTATION WHERE Model = ? AND Body = ?",
                (self.mod, self.body),
            ).fetchall()
        self.main(result, (2, 4, 5), "complectation")
        self.label_2.setText("Комплектация Автомобиля")

    def show_window4(self) -> None:
        """Открывает шаг выбора двигателя."""
        button = QApplication.instance().sender()
        complectation = button.text().split("\n")[0]
        from app.steps_equip import Engine
        self._open(Engine(self.mod, self.body, complectation))

    def back(self) -> None:
        """Возвращается к выбору кузова."""
        self._open(Body(self.mod))
