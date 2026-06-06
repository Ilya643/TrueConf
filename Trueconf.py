import sys
import sqlite3
import time
import os
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QApplication,
                             QTextEdit, QComboBox, QSizePolicy, QLineEdit)
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont, QPainter
from PyQt5.QtCore import Qt, QPoint, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
import DBUPDATE
import datetime
import re
import webbrowser


class Window(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("./ui/window.ui", self)

    def initUI(self):
        self.setWindowTitle('Trueconf')

    def main(self, result, s, w):
        widget = QWidget()
        vbox = QVBoxLayout()
        self.label.setText(brand)

        for i in result:
            hbox = QHBoxLayout()
            hbox.addStretch()

            labelP = QLabel(self)
            path = os.path.normpath(i[s[2]])
            pixmap = QPixmap(path)

            if pixmap.isNull():
                print("Не удалось загрузить:", path)

            width, hieght = pixmap.width(), pixmap.height()
            if width > 800:
                k = width / 786
                pixmap = pixmap.scaled(int(width / k), int(hieght / k))
            elif hieght > 400:
                k = hieght / 396
                pixmap = pixmap.scaled(int(width / k), int(hieght / k))

            labelP.setPixmap(pixmap)
            hbox.addWidget(labelP)
            hbox.addSpacing(20)

            m_inf = QVBoxLayout()
            m_inf.addStretch()
            text = i[s[0]]
            if len(text) > 32:
                text = f'{text[:30]}\n{text[30:]}'

            btn = QPushButton(f'{text}\nот {price_proc(i[s[1]])} ₽', self)
            btn.setMinimumSize(430, 70)
            btn.setFont(QFont('Arial', 20))
            m_inf.addWidget(btn)

            if w == 'model':
                btn.clicked.connect(self.show_window2)
            elif w == 'body':
                btn.clicked.connect(self.show_window3)
            elif w == 'complectation':
                global compl_inf
                btn.clicked.connect(self.show_window4)
                compl_inf = i[3]
                m_inf.addSpacing(20)
                subtitle = QLabel('Особенности:', self)
                subtitle.setFont(QFont('Arial', 16))
                m_inf.addWidget(subtitle)

                logWidget = QTextEdit()
                logWidget.setMinimumSize(500, 0)
                logWidget.setReadOnly(True)
                for f in i[3].split('*'):
                    logWidget.append(f'● {f}')
                logWidget.setFont(QFont('Arial', 15))
                m_inf.addWidget(logWidget)
            elif w == 'engine':
                btn.clicked.connect(self.show_window5)
            elif w == 'options':
                btn.clicked.connect(self.choice)
                self.pixmaps[btn] = [i[s[2]], labelP]
                m_inf.addSpacing(20)
                subtitle = QLabel('Особенности:', self)
                subtitle.setFont(QFont('Arial', 16))
                m_inf.addWidget(subtitle)
                logWidget = QTextEdit()
                logWidget.setMinimumSize(500, 0)
                logWidget.setReadOnly(True)
                for f in i[4].split('*'):
                    logWidget.append(f'● {f}')
                logWidget.setFont(QFont('Arial', 15))
                m_inf.addWidget(logWidget)
            elif w == 'color':
                btn.clicked.connect(self.show_window7)
                self.image[btn] = i[s[2]]

            m_inf.addStretch()
            hbox.addItem(m_inf)
            hbox.addStretch()
            vbox.addItem(hbox)
            vbox.addSpacing(20)

        widget.setLayout(vbox)
        self.scroll.setWidget(widget)
        self.showMaximized()

    def main_window(self):
        self.w = Main_window()
        self.w.show()
        self.hide()

    def db_error(self):
        labelop = QLabel(
            'ДЛЯ КОРРЕКТНОЙ РАБОТЫ ЗАГРУЗИТЕ ДАННЫЕ В РАЗДЕЛЕ "Настройки" ИЗ ГЛАВНОГО МЕНЮ',
            self)
        labelop.setFont(QFont('Arial', 20))
        labelop.setAlignment(Qt.AlignCenter)
        self.scroll.setWidget(labelop)
        self.showMaximized()


class Main_window(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("./ui/mainmm.ui", self)
        self.showFullScreen()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Конфигуратор LADA')
        self.pushButton.clicked.connect(self.show_window1)
        self.pushButton_2.clicked.connect(self.end)
        self.pushButton_3.clicked.connect(self.shsettings)
        self.pushButton_4.clicked.connect(
            lambda: webbrowser.open('https://t.me/Lil_soupchik'))

        for i in DBUPDATE.brands:
            self.comboBox.addItem(i, DBUPDATE.brands[i])

    def show_window1(self):
        global db, brand
        db, brand = self.comboBox.currentData(), self.comboBox.currentText()
        self.w = Model()
        self.w.show()
        self.hide()

    def shsettings(self):
        self.w = Settings()
        self.w.show()
        self.hide()

    def end(self):
        self.close()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QPainter(self)
        pixmap = QPixmap(
            "./36731-predstavitelskij_avtomobil-koleso-audi-sportkar-doroga-1920x1080.jpg")
        painter.drawPixmap(self.rect(), pixmap)


class Model(Window):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        super(Model, self).initUI()
        self.pushButton.clicked.connect(self.back)
        self.pushButton_2.setStyleSheet("background-color: #A92E18;")
        self.model()

    def model(self):
        if os.path.exists(db):
            con = sqlite3.connect(db)
            cur = con.cursor()
            result = cur.execute("""SELECT * FROM Model""").fetchall()
            con.close()
            super(Model, self).main(result, (0, 1, 2), 'model')
            self.label_2.setText('Семейство и Модель')
        else:
            self.db_error()

    def show_window2(self):
        button = QApplication.instance().sender()
        model = button.text().split('\n')[0].replace('Семейство ', '')
        self.w = Body(model)
        self.w.show()
        self.hide()

    def back(self):
        self.w = Main_window()
        self.w.show()
        self.hide()


class Body(Window):
    def __init__(self, model):
        self.model = model
        super().__init__()
        self.initUI()

    def initUI(self):
        super(Body, self).initUI()
        self.pushButton.clicked.connect(self.main_window)
        self.pushButton_2.setStyleSheet("background-color: #A92E18;")
        self.pushButton_2.setText(f'01 {self.model}')
        self.pushButton_3.setStyleSheet("background-color: #A92E18;")
        self.pushButton_2.clicked.connect(self.back)
        self.body()

    def body(self):
        m = self.model
        if os.path.exists(db):
            con = sqlite3.connect(db)
            cur = con.cursor()
            result = cur.execute(
                f"""SELECT * FROM BODY WHERE Model = '{m}'""").fetchall()
            con.close()
            super(Body, self).main(result, (1, 2, 3), 'body')
            self.label_2.setText('Кузов Автомобиля')
        else:
            self.db_error()

    def show_window3(self):
        button = QApplication.instance().sender()
        model = self.model
        self.w = Complectation(model, button.text().split('\n')[0])
        self.w.show()
        self.hide()

    def back(self):
        self.w = Model()
        self.w.show()
        self.hide()


class Complectation(Window):
    def __init__(self, *data):
        self.mod = data[0]
        self.body = data[1]
        super().__init__()
        self.initUI()

    def initUI(self):
        super(Complectation, self).initUI()
        self.pushButton.clicked.connect(self.main_window)
        self.pushButton_2.setStyleSheet("background-color: #A92E18;")
        self.pushButton_2.setText(f'01 {self.mod}')
        self.pushButton_3.setText(f'02 {self.body}')
        self.pushButton_3.setStyleSheet("background-color: #A92E18;")
        self.pushButton_3.clicked.connect(self.back)
        self.pushButton_4.setStyleSheet("background-color: #A92E18;")
        self.equip()

    def equip(self):
        m = self.mod
        body = self.body
        if os.path.exists(db):
            con = sqlite3.connect(db)
            cur = con.cursor()
            result = cur.execute(
                f"""SELECT * FROM COMPLECTATION WHERE Model = '{m}' AND Body = '{body}'""").fetchall()
            con.close()
            super(Complectation, self).main(result, (2, 4, 5), 'complectation')
            self.label_2.setText('Комплектация Автомобиля')
        else:
            self.db_error()

    def show_window4(self):
        button = QApplication.instance().sender()
        text = button.text().split('\n')
        self.w = Engine(self.mod, self.body, text[0])
        self.w.show()
        self.hide()

    def back(self):
        self.w = Body(self.mod)
        self.w.show()
        self.hide()


class Engine(Window):
    def __init__(self, *data):
        self.mod = data[0]
        self.body = data[1]
        self.equip = data[2]
        super().__init__()
        self.initUI()

    def initUI(self):
        super(Engine, self).initUI()
        self.pushButton.clicked.connect(self.main_window)
        self.pushButton_2.setStyleSheet("background-color: #A92E18;")
        self.pushButton_2.setText(f'01 {self.mod}')
        self.pushButton_3.setText(f'02 {self.body}')
        self.pushButton_4.setText(f'03 {self.equip}')
        self.pushButton_3.setStyleSheet("background-color: #A92E18;")
        self.pushButton_4.clicked.connect(self.back)
        self.pushButton_4.setStyleSheet("background-color: #A92E18;")
        self.pushButton_5.setStyleSheet("background-color: #A92E18;")
        self.engine()

    def engine(self):
        model = self.mod
        body = self.body
        equip = self.equip
        if os.path.exists(db):
            con = sqlite3.connect("lada.db")
            cur = con.cursor()
            result = cur.execute(
                f"""SELECT * FROM EQUIPMENT WHERE Model = '{model}' AND Body = '{body}' AND Complectation = '{equip}' AND Option = 'двигатель'""").fetchall()
            con.close()
            super(Engine, self).main(result, (4, 5, 6), 'engine')
            self.label_2.setText('Двигатель Автомобиля')
        else:
            self.db_error()

    def show_window5(self):
        button = QApplication.instance().sender()
        text = button.text().split('\n')
        price = [int(text[1].replace(' ', '').replace('от', '')[:-1])]
        self.w = Options(self.mod, self.body, self.equip, [text[0]], price)
        self.w.show()
        self.hide()

    def back(self):
        self.w = Complectation(self.mod, self.body)
        self.w.show()
        self.hide()


class Options(Window):
    def __init__(self, *data):
        self.mod = data[0]
        self.body = data[1]
        self.equip = data[2]
        self.characteristic = data[3]
        self.price = data[4]
        self.pixmaps = {}
        self.count = {}
        super().__init__()
        self.initUI()

    def initUI(self):
        super(Options, self).initUI()
        self.pushButton.clicked.connect(self.main_window)
        self.pushButton_2.setStyleSheet("background-color: #A92E18;")
        self.pushButton_2.setText(f'01 {self.mod}')
        self.pushButton_3.setText(f'02 {self.body}')
        self.pushButton_3.setStyleSheet("background-color: #A92E18;")
        self.pushButton_4.setText(f'03 {self.equip}')
        self.pushButton_4.setStyleSheet("background-color: #A92E18;")
        self.pushButton_5.clicked.connect(self.back)
        self.pushButton_5.setStyleSheet("background-color: #A92E18;")
        self.pushButton_6.setStyleSheet("background-color: #A92E18;")
        self.options()

    def options(self):
        model = self.mod
        body = self.body
        equip = self.equip
        if os.path.exists(db):
            con = sqlite3.connect("lada.db")
            cur = con.cursor()
            result = cur.execute(
                f"""SELECT * FROM EQUIPMENT WHERE Model = '{model}' AND Body = '{body}' AND Complectation = '{equip}' AND Option != 'двигатель'""").fetchall()
            con.close()
        else:
            self.db_error()

        self.label_2.setText('Дополнительные Опции')
        if result:
            super(Options, self).main(result, (3, 5, 6), 'options')
        else:
            labelop = QLabel(
                'ДОПОЛНИТЕЛЬНЫХ ОПЦИЙ ДЛЯ ДАННОГО АВТОМОБИЛЯ НЕ ПРЕДУСМОТРЕНО',
                self)
            labelop.setFont(QFont('Arial', 20))
            labelop.setAlignment(Qt.AlignCenter)
            self.scroll.setWidget(labelop)
            self.label.setText(brand)
            self.showMaximized()

        next_btn = QPushButton(f'Далее ❯', self)
        next_btn.setMinimumSize(200, 50)
        next_btn.setFont(QFont('Arial', 17))
        next_btn.clicked.connect(self.show_window6)
        self.horizontalLayout.addWidget(next_btn)

    def show_window6(self):
        for i in self.count:
            if self.count[i] % 2 != 0:
                name, price = i.text().split('\n')
                price = int(price.replace(' ', '').replace('от', '')[:-1])
                self.characteristic.append(name)
                self.price.append(int(price))
        self.w = Color(self.mod, self.body, self.equip, self.characteristic,
                       self.price)
        self.w.show()
        self.hide()

    def choice(self):
        button = QApplication.instance().sender()
        if button in self.count:
            self.count[button] += 1
        else:
            self.count[button] = 1
        i, labelP = self.pixmaps[button]
        path = os.path.normpath(i)
        pixmap = QPixmap(path)
        if pixmap.isNull():
            print("Не удалось загрузить:", path)
        width, hieght = pixmap.width(), pixmap.height()
        if width > 800:
            k = width / 786
            pixmap = pixmap.scaled(int(width / k), int(hieght / k))
        elif hieght > 400:
            k = hieght / 396
            pixmap = pixmap.scaled(int(width / k), int(hieght / k))
        if self.count[button] % 2 != 0:
            painter = QPainter(pixmap)
            font = QFont()
            font.setPointSize(16)
            painter.setFont(font)
            painter.drawText(QPoint(20, 36), '✅')
            painter.end()
            labelP.setPixmap(pixmap)
        else:
            labelP.setPixmap(pixmap)

    def back(self):
        self.w = Engine(self.mod, self.body, self.equip)
        self.w.show()
        self.hide()


class Color(Window):
    def __init__(self, *data):
        self.mod = data[0]
        self.body = data[1]
        self.equip = data[2]
        self.characteristic = data[3]
        self.price = data[4]
        self.image = {}
        super().__init__()
        self.initUI()

    def initUI(self):
        super(Color, self).initUI()
        self.pushButton.clicked.connect(self.main_window)
        self.pushButton_2.setStyleSheet("background-color: #A92E18;")
        self.pushButton_2.setText(f'01 {self.mod}')
        self.pushButton_3.setText(f'02 {self.body}')
        self.pushButton_3.setStyleSheet("background-color: #A92E18;")
        self.pushButton_4.setText(f'03 {self.equip}')
        self.pushButton_4.setStyleSheet("background-color: #A92E18;")
        self.pushButton_5.setStyleSheet("background-color: #A92E18;")
        self.pushButton_6.clicked.connect(self.back)
        self.pushButton_6.setStyleSheet("background-color: #A92E18;")
        self.pushButton_7.setStyleSheet("background-color: #A92E18;")
        self.color()

    def color(self):
        if os.path.exists(db):
            con = sqlite3.connect("lada.db")
            cur = con.cursor()
            result = cur.execute(
                f"""SELECT * FROM Color WHERE Model = '{self.mod}' AND Body = '{self.body}' AND Complectation = '{self.equip}'""").fetchall()
            con.close()
            super(Color, self).main(result, (3, 4, 5), 'color')
            self.label_2.setText('Цвет Автомобиля')
        else:
            self.db_error()

    def show_window7(self):
        button = QApplication.instance().sender()
        text = button.text().split('\n')
        self.characteristic.append(''.join(text[:-1]))
        self.price.append(
            int(text[-1].replace(' ', '').replace('от', '')[:-1]))
        self.image = self.image[button]
        self.w = In_total(self.mod, self.body, self.equip, self.price,
                          self.characteristic, self.image)
        self.w.show()
        self.hide()

    def main_window(self):
        self.w = Main_window()
        self.w.show()
        self.hide()

    def back(self):
        self.w = Options(self.mod, self.body, self.equip, self.characteristic,
                         self.price)
        self.w.show()
        self.hide()


class In_total(QWidget):
    def __init__(self, *data):
        self.data = data
        print(self.data)
        super().__init__()
        uic.loadUi("./ui/fwindow.ui", self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Trueconf')
        self.pushButton.clicked.connect(self.main_window)
        self.In_total()

    def In_total(self):
        path = os.path.normpath(self.data[5])
        pixmap = QPixmap(path)
        if pixmap.isNull():
            print("Не удалось загрузить:", path)
        self.label.setPixmap(pixmap)
        self.label.setAlignment(Qt.AlignCenter)
        self.label_2.setText(f'Цена вашего автомобиля - {self.data[0]}')
        self.label_3.setText(f'{price_proc(sum(self.data[3]))} ₽')
        self.label_7.setText(f'{self.data[1]} {self.data[2]}')
        self.label_8.setText(f'{price_proc(self.data[3][0])} ₽')
        self.label_5.setText(f'{self.data[4][0]}')
        self.label_9.setText(f'{price_proc(sum(self.data[3][1:-1]))} ₽')
        self.label_11.setText(f'{price_proc(self.data[3][-1])} ₽')

        self.pushButton_2.setText('Карта дилеров')
        self.pushButton_2.clicked.connect(self.map)

        self.pushButton_3.setText('🔍 Поиск аналогов')
        self.pushButton_3.clicked.connect(self.show_analogs)
        self.pushButton_3.setStyleSheet(
            "background-color: #2E8B57; color: white;")

        self.showMaximized()
        self.doptions()
        self.options()

    def doptions(self):
        dop = QHBoxLayout()
        name = QVBoxLayout()
        price = QVBoxLayout()
        names_inf, price_inf = self.data[4][1:-1], self.data[3][1:-1]
        for iop in range(len(names_inf)):
            n = QLabel(f'● {names_inf[iop]}', self)
            n.setFont(QFont('Arial', 14))
            name.addWidget(n)
            p = QLabel(f'{price_proc(price_inf[iop])} ₽', self)
            p.setFont(QFont('Arial', 14))
            price.addWidget(p)
        dop.addItem(name)
        dop.addSpacing(10)
        dop.addItem(price)
        self.widget = QWidget()
        self.widget.setLayout(dop)
        self.verticalLayout_4.addWidget(self.widget)

    def options(self):
        dop = QHBoxLayout()
        name = QVBoxLayout()
        for op in compl_inf.split('*'):
            if len(op) > 32:
                if op[29] == ' ':
                    op = f'{op[:30]}\n{op[30:]}'
                else:
                    op = f'{op[:30]}-\n{op[30:]}'
            n = QLabel(f'● {op}', self)
            n.setFont(QFont('Arial', 14))
            name.addWidget(n)
        dop.addItem(name)
        widget = QWidget()
        widget.setLayout(dop)
        self.verticalLayout_5.addWidget(widget)

    def main_window(self):
        self.w = Main_window()
        self.w.show()
        self.hide()

    def map(self):
        city = getattr(self, 'city', 'Москва')
        self.w = Dealers_map(city=city)
        self.w.show()

    def show_analogs(self):
        """Открывает окно с поиском аналогов на Auto.ru"""
        # Правильно извлекаем данные:
        model = self.data[0]  # 'Granta'
        body_full = self.data[1]  # 'Granta седан'
        # Тип кузова – последнее слово (например, 'седан')
        body_type = body_full.split()[-1] if len(
            body_full.split()) > 1 else body_full
        equip = self.data[2]  # 'Стандарт Плюс'
        price = self.data[3]  # [850000, 0]
        characteristics = self.data[
            4]  # ['1.6 л (90 л.с.)', 'Белый "Ледниковый" (221)']
        image = self.data[5]

        self.w = AnalogSearch(
            model=model,
            body=body_type,
            equip=equip,
            price=price,
            characteristics=characteristics,
            image_path=image
        )
        self.w.show()


class Dealers_map(QWidget):
    def __init__(self, city="Москва"):
        super().__init__()
        self.city = city
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Карта дилеров LADA')
        self.resize(1024, 680)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)

        self.city_input = QLineEdit(self)
        self.city_input.setText(self.city)
        self.city_input.setPlaceholderText('Введите город...')
        self.city_input.setMaximumHeight(32)
        self.city_input.returnPressed.connect(self.search)
        search_layout.addWidget(self.city_input, 1)

        btn = QPushButton('🔍 Найти', self)
        btn.setMaximumHeight(32)
        btn.clicked.connect(self.search)
        search_layout.addWidget(btn)
        layout.addLayout(search_layout)

        self.web = QWebEngineView()
        layout.addWidget(self.web, 1)
        self.load_map(self.city)
        self.show()

    def search(self):
        city = self.city_input.text().strip()
        if city:
            self.city = city
            self.load_map(city)

    def load_map(self, city):
        safe_city = city.replace("'", "\\'").replace('"', '\\"')
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <script src="https://api-maps.yandex.ru/2.1/?apikey=7fbf4c89-a94f-4112-97d3-888bda8facb5&lang=ru_RU"></script>
            <style>
                html, body, #map {{ width: 100%; height: 100%; margin: 0; padding: 0; }}
                .status {{
                    position: absolute; top: 10px; left: 50%; transform: translateX(-50%);
                    background: #fff; padding: 8px 16px; border-radius: 20px;
                    font-family: Arial, sans-serif; font-size: 13px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.15); z-index: 1000;
                    white-space: nowrap;
                }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <div class="status" id="status">🔍 Поиск дилеров LADA в г. {safe_city}...</div>
            <script>
                ymaps.ready(init);
                function init() {{
                    var myMap = new ymaps.Map("map", {{
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
                        var status = document.getElementById('status');
                        if (count > 0) {{
                            status.textContent = '✅ Найдено: ' + count + ' дилеров LADA';
                            var bounds = searchControl.getResults().getBounds();
                            myMap.setBounds(bounds, {{ checkZoomRange: true, zoomMargin: 40 }});
                        }} else {{
                            status.textContent = '❌ Дилеры не найдены. Проверьте название города.';
                        }}
                    }});
                    searchControl.search('автосалон LADA {safe_city}');
                    myMap.controls.add(searchControl);
                    setTimeout(function() {{
                        var input = document.querySelector('.ymaps-2-1-79-search-control__input');
                        if (input) input.style.display = 'none';
                    }}, 500);
                }}
            </script>
        </body>
        </html>
        """
        self.web.setHtml(html)


class AnalogSearch(QWidget):
    """Окно поиска аналогов на Auto.ru (цена, кузов, объём двигателя)"""

    def __init__(self, model, body, equip, price, characteristics, image_path):
        super().__init__()
        self.model = model             
        self.body = body                  
        self.equip = equip
        self.base_price = price[0] if price else 0
        self.characteristics = characteristics  
        self.image_path = image_path

        # Настройка User-Agent
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        profile.setHttpAcceptLanguage("ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7")

        self.url = self._build_autoru_url()
        print("=== AUTO.RU URL ===")
        print(self.url)
        print("===================")

        try:
            self.initUI()
            self.load_url()
        except Exception as e:
            print("Ошибка WebEngine, открываю системный браузер:", e)
            webbrowser.open(self.url)
            self.close()

    def initUI(self):
        self.setWindowTitle('🔍 Поиск аналогов на Auto.ru')
        self.resize(1200, 800)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        top_layout = QHBoxLayout()
        info_label = QLabel(
            f'{self.model} {self.body} • от {price_proc(self.base_price)} ₽')
        info_label.setFont(QFont('Arial', 12))
        top_layout.addWidget(info_label)
        top_layout.addStretch()

        refresh_btn = QPushButton('🔄 Обновить')
        refresh_btn.clicked.connect(lambda: self.web_auto.reload())
        top_layout.addWidget(refresh_btn)

        open_browser_btn = QPushButton('🌐 Открыть в браузере')
        open_browser_btn.clicked.connect(lambda: webbrowser.open(self.url))
        top_layout.addWidget(open_browser_btn)

        main_layout.addLayout(top_layout)

        self.web_auto = QWebEngineView()
        main_layout.addWidget(self.web_auto, 1)

        self.status_bar = QLabel('Загрузка...')
        self.status_bar.setAlignment(Qt.AlignCenter)
        self.status_bar.setStyleSheet("background: #f0f0f0; padding: 4px; color: #555;")
        main_layout.addWidget(self.status_bar)

        self.show()

    def load_url(self):
        self.status_bar.setText('Загрузка Auto.ru...')
        QApplication.processEvents()
        self.web_auto.load(QUrl(self.url))
        self.web_auto.loadFinished.connect(self._on_loaded)

    def _build_autoru_url(self):
        """Формирует URL с фильтрами: цена, кузов, объём двигателя (без года и пробега)"""
        base = "https://auto.ru/cars/vaz/"

        # Модель в пути
        model_map = {
            'granta': 'granta/',
            'vesta': 'vesta/',
            'largus': 'largus/',
            'niva': 'niva/',
            'xray': 'xray/',
            'priora': 'priora/',
            'aura': 'aura/',
        }
        model_lower = self.model.lower()
        model_path = ''
        for key, path in model_map.items():
            if key in model_lower:
                model_path = path
                break
        if not model_path:
            return "https://auto.ru/cars/vaz/used/"

        base += model_path + "used/"

        body_lower = self.body.lower()
        body_map = {
            'седан': 'sedan',
            'хэтчбек': 'hatchback',
            'универсал': 'universal',
            'внедорожник': 'suv',
            'джип': 'suv',
            'кроссовер': 'crossover',
            'лифтбек': 'liftback',
        }
        body_val = next((v for k, v in body_map.items() if k in body_lower), None)
        if body_val:
            base += f"body-{body_val}/"

        params = []

        min_p = int(self.base_price * 0.7)
        max_p = int(self.base_price * 1.3)
        params.append(f"price_from={min_p}")
        params.append(f"price_to={max_p}")

        displacement_from = None
        displacement_to = None
        for char in self.characteristics:
            match = re.search(r'(\d+\.?\d*)\s*л', char)
            if match:
                disp = float(match.group(1))
                delta = max(0.1, disp * 0.1)
                displacement_from = round(disp - delta, 1)
                displacement_to = round(disp + delta, 1)
                break
        if displacement_from is not None:
            params.append(f"displacement_from={displacement_from}")
            params.append(f"displacement_to={displacement_to}")

        params.append("sort=cr_date-desc")

        return base + "?" + "&".join(params)

    def _on_loaded(self, ok):
        if ok:
            self.status_bar.setText('Auto.ru загружен')
        else:
            self.status_bar.setText('Ошибка загрузки! Нажмите "Открыть в браузере".')

class Settings(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("./ui/settings.ui", self)
        self.initUI()

    def initUI(self):
        self.setFixedSize(700, 500)
        self.setWindowTitle('Настройки')
        self.pushButton_3.clicked.connect(self.update)
        self.pushButton_4.clicked.connect(self.back)

    def update(self):
        global timeup
        if time.monotonic() - timeup > 1800:
            w = Load()
            w.show()
            self.hide()
            DBUPDATE.all_update(self.checkBox.isChecked(),
                                self.checkBox_2.isChecked())
            timeup = time.monotonic()
            self.show()
            w.close()

    def back(self):
        self.w = Main_window()
        self.w.show()
        self.hide()


class Load(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("./ui/load.ui", self)
        self.setWindowTitle('Ожидайте окончания загрузки')
        self.setFixedSize(400, 1)


# Глобальные переменные
db, brand = None, None
timeup = -1801
compl_inf = ''


def price_proc(price):
    """Форматирует цену с пробелами (1 000 000)"""
    price = str(price)
    new_price = ''
    for ind in range(len(price)):
        if (ind + 1) % 3 == 0:
            new_price += f'{price[len(price) - ind - 1]} '
        else:
            new_price += price[len(price) - ind - 1]
    return new_price[::-1]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main_window()
    ex.show()
    sys.exit(app.exec_())