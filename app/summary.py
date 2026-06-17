"""
Итоговое окно конфигуратора.

Содержит класс ``InTotal`` — финальный экран с полной ценой,
детализацией опций и кнопками перехода к карте дилеров
и поиску аналогов на Auto.ru.

Класс ``AnalogSearch`` вынесен в ``app.analogs``.
"""

import os

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (
    QHBoxLayout, QLabel, QVBoxLayout, QWidget,
)

import app.utils as state
from app.utils import price_proc


class InTotal(QWidget):
    """Итоговое окно — сводка конфигурации и стоимости.

    Отображает:
    * фото выбранного цвета;
    * суммарную цену и разбивку по категориям;
    * список особенностей комплектации;
    * кнопки «Карта дилеров» и «Поиск аналогов».

    Args:
        model: Название модели.
        body: Название кузова.
        equip: Название комплектации.
        prices: [базовая_цена, *цены_опций, цена_цвета].
        characteristics: [двигатель, *опции, цвет].
        image_path: Путь к фото выбранного цвета.
    """

    def __init__(self, model: str, body: str, equip: str,
                 prices: list, characteristics: list, image_path: str) -> None:
        """Сохраняет данные и инициализирует окно."""
        super().__init__()
        self.model = model
        self.body = body
        self.equip = equip
        self.prices = prices
        self.characteristics = characteristics
        self.image_path = image_path
        uic.loadUi("./ui/fwindow.ui", self)
        self._init_ui()

    def _init_ui(self) -> None:
        """Заполняет все поля итогового окна."""
        self.setWindowTitle("Trueconf")
        self.pushButton.clicked.connect(self._back_to_main)

        # Фото выбранного цвета
        self.label.setPixmap(QPixmap(os.path.normpath(self.image_path)))
        self.label.setAlignment(Qt.AlignCenter)

        # Текстовые поля с ценами и названиями
        self.label_2.setText(f"Цена вашего автомобиля - {self.model}")
        self.label_3.setText(f"{price_proc(sum(self.prices))} ₽")
        self.label_7.setText(f"{self.body} {self.equip}")
        self.label_8.setText(f"{price_proc(self.prices[0])} ₽")
        self.label_5.setText(f"{self.characteristics[0]}")
        self.label_9.setText(f"{price_proc(sum(self.prices[1:-1]))} ₽")
        self.label_11.setText(f"{price_proc(self.prices[-1])} ₽")

        # Кнопка «Карта дилеров»
        self.pushButton_2.setText("Карта дилеров")
        self.pushButton_2.clicked.connect(self._show_map)

        # Кнопка «Поиск аналогов»
        self.pushButton_3.setText("🔍 Поиск аналогов")
        self.pushButton_3.setStyleSheet("background-color: #2E8B57; color: white;")
        self.pushButton_3.clicked.connect(self._show_analogs)

        self.showMaximized()
        self._render_options()
        self._render_features()

    def _render_options(self) -> None:
        """Строит двухколоночный список выбранных опций (название + цена)."""
        row = QHBoxLayout()
        names_col, prices_col = QVBoxLayout(), QVBoxLayout()

        for name, price in zip(self.characteristics[1:-1], self.prices[1:-1]):
            lbl_n = QLabel(f"● {name}", self)
            lbl_n.setFont(QFont("Arial", 14))
            names_col.addWidget(lbl_n)
            lbl_p = QLabel(f"{price_proc(price)} ₽", self)
            lbl_p.setFont(QFont("Arial", 14))
            prices_col.addWidget(lbl_p)

        row.addItem(names_col)
        row.addSpacing(10)
        row.addItem(prices_col)
        container = QWidget()
        container.setLayout(row)
        self.verticalLayout_4.addWidget(container)

    def _render_features(self) -> None:
        """Отображает маркированный список особенностей комплектации."""
        col = QVBoxLayout()
        for feature in state.compl_inf.split("*"):
            # Перенос длинной строки для читаемости
            if len(feature) > 32:
                sep = 30
                sep_char = "\n" if feature[sep - 1] == " " else "-\n"
                feature = feature[:sep] + sep_char + feature[sep:]
            lbl = QLabel(f"● {feature}", self)
            lbl.setFont(QFont("Arial", 14))
            col.addWidget(lbl)
        container = QWidget()
        container.setLayout(col)
        self.verticalLayout_5.addWidget(container)

    def _back_to_main(self) -> None:
        """Возвращает пользователя в главное меню."""
        from app.main_window import MainWindow
        self.w = MainWindow()
        self.w.show()
        self.hide()

    def _show_map(self) -> None:
        """Открывает карту дилеров."""
        from app.dealers import DealersMap
        self.w = DealersMap()
        self.w.show()

    def _show_analogs(self) -> None:
        """Открывает окно поиска аналогов на Auto.ru."""
        from app.analogs import AnalogSearch
        body_parts = self.body.split()
        body_type = body_parts[-1] if len(body_parts) > 1 else self.body
        self.w = AnalogSearch(
            model=self.model,
            body=body_type,
            prices=self.prices,
            characteristics=self.characteristics,
        )
        self.w.show()
