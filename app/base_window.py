"""
Базовый класс окна-шага конфигуратора.

Содержит универсальный метод ``main`` для отрисовки карточек
выбора (модель, кузов, комплектация, двигатель, опции, цвет),
а также вспомогательные методы навигации и обработки ошибок.
"""

import os

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import app.utils as state
from app.utils import price_proc


# Вспомогательная функция масштабирования изображений
def _scale_pixmap(pixmap: QPixmap, max_w: int = 800, max_h: int = 400) -> QPixmap:
    """Масштабирует QPixmap с сохранением пропорций.

    Уменьшает изображение, если оно превышает допустимые размеры.
    Исходное изображение не увеличивается.

    Args:
        pixmap: Исходный объект QPixmap.
        max_w: Максимальная допустимая ширина (пиксели).
        max_h: Максимальная допустимая высота (пиксели).

    Returns:
        Масштабированный (или исходный) QPixmap.
    """
    w, h = pixmap.width(), pixmap.height()
    if w > max_w:
        k = w / (max_w - 14)
        return pixmap.scaled(int(w / k), int(h / k))
    if h > max_h:
        k = h / (max_h - 4)
        return pixmap.scaled(int(w / k), int(h / k))
    return pixmap


# Базовый класс
class Window(QWidget):
    """Базовый класс для всех шагов конфигуратора.

    Загружает общий UI-файл ``window.ui`` и предоставляет метод
    ``main`` для динамической генерации карточек выбора.
    Дочерние классы переопределяют методы ``show_window*`` для
    перехода на следующий шаг.
    """

    def __init__(self) -> None:
        """Инициализирует виджет и загружает UI-макет из файла."""
        super().__init__()
        uic.loadUi("./ui/window.ui", self)

    def initUI(self) -> None:
        """Задаёт заголовок окна."""
        self.setWindowTitle("Trueconf")


    # Генерация карточек
    def main(self, result: list, s: tuple, w: str) -> None:
        """Генерирует список карточек выбора внутри прокручиваемой области.

        Для каждой строки из ``result`` создаётся горизонтальный блок:
        изображение слева, кнопка + описание справа.

        Args:
            result: Список кортежей из базы данных (строки SELECT).
            s: Кортеж из трёх индексов ``(name_idx, price_idx, img_idx)``
               для доступа к соответствующим полям строки.
            w: Тип текущего шага - ``'model'``, ``'body'``,
               ``'complectation'``, ``'engine'``, ``'options'`` или ``'color'``.
        """
        container = QWidget()
        vbox = QVBoxLayout()
        self.label.setText(state.brand)

        for row in result:
            hbox = QHBoxLayout()
            hbox.addStretch()

            # Изображение
            img_label = QLabel(self)
            raw_path = row[s[2]]
            if raw_path:
                path = os.path.normpath(raw_path)
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    pixmap = _scale_pixmap(pixmap)
                    img_label.setPixmap(pixmap)
            hbox.addWidget(img_label)
            hbox.addSpacing(20)

            # Информационный блок (кнопка + детали)
            info_layout = QVBoxLayout()
            info_layout.addStretch()

            name_text = row[s[0]]
            # Переносим длинные названия на новую строку для читаемости кнопки
            if len(name_text) > 32:
                name_text = f"{name_text[:30]}\n{name_text[30:]}"

            btn = QPushButton(
                f"{name_text}\nот {price_proc(row[s[1]])} ₽", self
            )
            btn.setMinimumSize(430, 70)
            btn.setFont(QFont("Arial", 20))
            info_layout.addWidget(btn)

            # Подключаем сигналы и добавляем доп. виджеты в зависимости от шага
            self._setup_card(btn, row, s, w, img_label, info_layout)

            info_layout.addStretch()
            hbox.addItem(info_layout)
            hbox.addStretch()
            vbox.addItem(hbox)
            vbox.addSpacing(20)

        container.setLayout(vbox)
        self.scroll.setWidget(container)
        self.showMaximized()

    def _setup_card(
        self,
        btn: QPushButton,
        row: tuple,
        s: tuple,
        w: str,
        img_label: QLabel,
        layout: QVBoxLayout,
    ) -> None:
        """Подключает обработчики и добавляет дополнительные виджеты к карточке.

        Внутренний метод, вызываемый из ``main``.  Определяет поведение
        кнопки и состав карточки в зависимости от типа шага ``w``.

        Args:
            btn: Кнопка карточки.
            row: Строка данных из БД.
            s: Индексы полей (name, price, img).
            w: Тип шага.
            img_label: QLabel с изображением (нужен для опций).
            layout: Вертикальный лейаут карточки.
        """
        if w == "model":
            btn.clicked.connect(self.show_window2)

        elif w == "body":
            btn.clicked.connect(self.show_window3)

        elif w == "complectation":
            btn.clicked.connect(self.show_window4)
            state.compl_inf = row[3]
            self._add_features_widget(row[3], layout)

        elif w == "engine":
            btn.clicked.connect(self.show_window5)

        elif w == "options":
            btn.clicked.connect(self.choice)
            # Сохраняем пару (путь_к_изображению, label) для toggle-эффекта
            self.pixmaps[btn] = [row[s[2]], img_label]
            self._add_features_widget(row[4], layout)

        elif w == "color":
            btn.clicked.connect(self.show_window7)
            self.image[btn] = row[s[2]]

    @staticmethod
    def _add_features_widget(features_str: str, layout: QVBoxLayout) -> None:
        """Добавляет в лейаут QTextEdit с маркированным списком особенностей.

        Args:
            features_str: Строка с особенностями, разделёнными символом «*».
            layout: Лейаут, в который добавляется виджет.
        """
        layout.addSpacing(20)
        subtitle = QLabel("Особенности:")
        subtitle.setFont(QFont("Arial", 16))
        layout.addWidget(subtitle)

        log_widget = QTextEdit()
        log_widget.setMinimumSize(500, 0)
        log_widget.setReadOnly(True)
        log_widget.setFont(QFont("Arial", 15))
        for feature in features_str.split("*"):
            log_widget.append(f"● {feature}")
        layout.addWidget(log_widget)


    # Навигация и ошибки
    def main_window(self) -> None:
        """Возвращает пользователя в главное меню приложения."""
        # Импорт здесь, чтобы избежать циклических зависимостей
        from app.main_window import MainWindow
        self._open(MainWindow())

    def db_error(self) -> None:
        """Отображает сообщение об отсутствии базы данных."""
        msg = QLabel(
            'ДЛЯ КОРРЕКТНОЙ РАБОТЫ ЗАГРУЗИТЕ ДАННЫЕ В РАЗДЕЛЕ "Настройки" '
            "ИЗ ГЛАВНОГО МЕНЮ",
            self,
        )
        msg.setFont(QFont("Arial", 20))
        msg.setAlignment(Qt.AlignCenter)
        self.scroll.setWidget(msg)
        self.showMaximized()

    def _open(self, window: QWidget) -> None:
        """Открывает новое окно и скрывает текущее.

        Args:
            window: Окно, которое нужно показать.
        """
        self.w = window
        self.w.show()
        self.hide()


    # Заглушки-переопределяемые методы навигации
    def show_window2(self) -> None:
        """Переходит на шаг выбора кузова. Переопределяется в Model."""

    def show_window3(self) -> None:
        """Переходит на шаг выбора комплектации. Переопределяется в Body."""

    def show_window4(self) -> None:
        """Переходит на шаг выбора двигателя. Переопределяется в Complectation."""

    def show_window5(self) -> None:
        """Переходит на шаг выбора опций. Переопределяется в Engine."""

    def show_window7(self) -> None:
        """Переходит на итоговое окно. Переопределяется в Color."""

    def choice(self) -> None:
        """Обрабатывает выбор/снятие дополнительной опции. Переопределяется в Options."""

    def back(self) -> None:
        """Возвращается на предыдущий шаг. Переопределяется в каждом шаге."""
