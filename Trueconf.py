import sys
import sqlite3
import time
import webbrowser
import os
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QApplication, QTextEdit
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFileDialog
from PyQt5.QtGui import QPixmap, QFont, QPainter
from PyQt5.QtCore import Qt, QPoint
import DBUPDATE


class Window(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("./ui/window.ui", self)

    def initUI(self):
        # даём название окну
        self.setWindowTitle('Trueconf')

    def main(self, result, s, w):
        # создаём widget и layout
        widget = QWidget()
        vbox = QVBoxLayout()
        self.label.setText(brand)

        # создаём список с моделями
        for i in result:
            hbox = QHBoxLayout()
            hbox.addStretch()

            # загружаем картинку
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
            # создаём кнопку
            text = i[s[0]]
            if len(text) > 32:
                text = f'{text[:30]}\n{text[30:]}'

            btn = QPushButton(f'{text}\nот {price_proc(i[s[1]])} ₽', self)
            btn.setMinimumSize(430, 70)
            # изменяем шрифт
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

        # создаём Layout
        widget.setLayout(vbox)
        # настраиваем Scroll
        self.scroll.setWidget(widget)
        self.showMaximized()

    def main_window(self):
        # открываем первое окно, закрыв текущее
        self.w = Main_window()
        self.w.show()
        self.hide()

    def db_error(self):
        labelop = QLabel('ДЛЯ КОРРЕКТНОЙ РАБОТЫ ЗАГРУЗИТЕ ДАННЫЕ В РАЗДЕЛЕ "Настройки" ИЗ ГЛАВНОГО МЕНЮ', self)
        labelop.setFont(QFont('Arial', 20))
        labelop.setAlignment(Qt.AlignCenter)
        self.scroll.setWidget(labelop)

        self.showMaximized()


class Main_window(QWidget):
    def __init__(self):
        super().__init__()
        # загрузка дизайна
        uic.loadUi("./ui/mainmm.ui", self)
        self.showFullScreen()
        self.initUI()

    def initUI(self):
        # фиксируем размеры окна
        # self.setFixedSize(700, 500)
        # даём название окну
        self.setWindowTitle('Конфигуратор LADA')

        # подключаем кнопки к функциям
        self.pushButton.clicked.connect(self.show_window1)
        self.pushButton_2.clicked.connect(self.end)
        self.pushButton_3.clicked.connect(self.shsettings)
        self.pushButton_4.clicked.connect(lambda: webbrowser.open('https://t.me/Lil_soupchik'))

        for i in DBUPDATE.brands:
            self.comboBox.addItem(i, DBUPDATE.brands[i])

    def show_window1(self):
        global db, brand
        db, brand = self.comboBox.currentData(), self.comboBox.currentText()
        # открываем новое окно
        self.w = Model()
        self.w.show()
        # закрываем старое окно
        self.hide()

    def shsettings(self):
        self.w = Settings()
        self.w.show()
        self.hide()

    def end(self):
        # заканчиваем работу программы
        self.close()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QPainter(self)
        pixmap = QPixmap("./36731-predstavitelskij_avtomobil-koleso-audi-sportkar-doroga-1920x1080.jpg")
        painter.drawPixmap(self.rect(), pixmap)


class Model(Window):
    def __init__(self):
        super().__init__()
        # загрузка дизайна
        self.initUI()

    def initUI(self):
        super(Model, self).initUI()
        # фиксируем размеры окна
        # self.setFixedSize(700, 500)
        # подключаем кнопки к функциям
        self.pushButton.clicked.connect(self.back)
        self.pushButton_2.setStyleSheet("background-color: #A92E18;")

        self.model()

    def model(self):
        # подключение к БД
        if os.path.exists(db):
            con = sqlite3.connect(db)
            # создание курсора
            cur = con.cursor()
            # выполнение запроса и получение всех результатов
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
        # получаем выбранную модель
        super().__init__()
        self.initUI()

    def initUI(self):
        super(Body, self).initUI()
        # фиксируем размеры окна
        # self.setFixedSize(700, 500)

        # подключаем кнопки к функциям
        self.pushButton.clicked.connect(self.main_window)
        self.pushButton_2.setStyleSheet("background-color: #A92E18;")
        self.pushButton_2.setText(f'01 {self.model}')
        self.pushButton_3.setStyleSheet("background-color: #A92E18;")
        self.pushButton_2.clicked.connect(self.back)

        self.body()

    def body(self):
        m = self.model
        if os.path.exists(db):
            # подключение к БД
            con = sqlite3.connect(db)
            # создание курсора
            cur = con.cursor()

            # выполнение запроса и получение всех результатов
            result = cur.execute(f"""SELECT * FROM BODY
                                   WHERE Model = '{m}'""").fetchall()
            con.close()

            super(Body, self).main(result, (1, 2, 3), 'body')
            self.label_2.setText('Кузов Автомобиля')
        else:
            self.db_error()

    def show_window3(self):
        button = QApplication.instance().sender()
        model = self.model

        # открываем следующее окно, закрыв текущее
        self.w = Complectation(model, button.text().split('\n')[0])
        self.w.show()
        self.hide()

    def back(self):
        # открываем прошлое окно, закрыв текущее
        self.w = Model()
        self.w.show()
        self.hide()


class Complectation(Window):
    def __init__(self, *data):
        self.mod = data[0]
        self.body = data[1]
        # получаем выбранную модель и корпус

        super().__init__()
        self.initUI()

    def initUI(self):
        super(Complectation, self).initUI()

        # подключаем кнопки к функциям
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
            # подключение к БД
            con = sqlite3.connect(db)
            # создание курсора
            cur = con.cursor()

            # выполнение запроса и получение всех результатов
            result = cur.execute(f"""SELECT * FROM COMPLECTATION
                                            WHERE Model = '{m}' AND Body = '{body}'""").fetchall()
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
        # открываем прошлое окно, закрыв текущее
        self.w = Body(self.mod)
        self.w.show()
        self.hide()


class Engine(Window):
    def __init__(self, *data):
        # получаем выбранную модель, корпус, комплектацию, цену
        self.mod = data[0]
        self.body = data[1]
        self.equip = data[2]
        super().__init__()
        self.initUI()

    def initUI(self):
        super(Engine, self).initUI()

        # подключаем кнопки к функциям
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
            # подключение к БД
            con = sqlite3.connect("lada.db")
            # создание курсора
            cur = con.cursor()

            # выполнение запроса и получение всех результатов
            result = cur.execute(f"""SELECT * FROM EQUIPMENT
                                                    WHERE Model = '{model}' AND Body = '{body}'
                                                    AND Complectation = '{equip}' AND Option = 'двигатель'""").fetchall()
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
        # открываем прошлое окно, закрыв текущее
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
        # получаем выбранную модель и корпус
        super().__init__()
        self.initUI()

    def initUI(self):
        super(Options, self).initUI()

        # подключаем кнопки к функциям
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
            # подключение к БД
            con = sqlite3.connect("lada.db")
            # создание курсора
            cur = con.cursor()

            # выполнение запроса и получение всех результатов
            result = cur.execute(f"""SELECT * FROM EQUIPMENT
                                                            WHERE Model = '{model}' AND Body = '{body}'
                                                            AND Complectation = '{equip}' AND Option != 'двигатель'""").fetchall()
            con.close()
        else:
            self.db_error()

        self.label_2.setText('Дополнительные Опции')
        if result:
            super(Options, self).main(result, (3, 5, 6), 'options')
        else:
            labelop = QLabel('ДОПОЛНИТЕЛЬНЫХ ОПЦИЙ ДЛЯ ДАННОГО АВТОМОБИЛЯ НЕ ПРЕДУСМОТРЕНО', self)
            labelop.setFont(QFont('Arial', 20))
            labelop.setAlignment(Qt.AlignCenter)
            self.scroll.setWidget(labelop)

            self.label.setText(brand)

            self.showMaximized()

        next = QPushButton(f'Далее ❯', self)
        next.setMinimumSize(200, 50)
        # изменяем шрифт
        next.setFont(QFont('Arial', 17))
        next.clicked.connect(self.show_window6)
        self.horizontalLayout.addWidget(next)

    def show_window6(self):
        options = []
        for i in self.count:
            if self.count[i] % 2 != 0:
                name, price = i.text().split('\n')
                price = int(price.replace(' ', '').replace('от', '')[:-1])
                self.characteristic.append(name)
                self.price.append(int(price))
                options.append(i.text())

        self.w = Color(self.mod, self.body, self.equip, self.characteristic, self.price)
        self.w.show()
        self.hide()

    def choice(self):
        button = QApplication.instance().sender()
        if button in self.count:
            count = self.count[button] + 1
            self.count[button] = count
        else:
            count = 1
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

        if count % 2 != 0:
            painter = QPainter(pixmap)

            font = QFont()
            font.setPointSize(16)
            painter.setFont(font)

            ypos, xpos = 36, 20
            pos = QPoint(xpos, ypos)
            painter.drawText(pos, '✅')
            painter.end()
            labelP.setPixmap(pixmap)
        else:
            labelP.setPixmap(pixmap)

    def back(self):
        # открываем прошлое окно, закрыв текущее
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
        # получаем выбранную модель, корпус, комплектацию, списоки оснащения и цен
        super().__init__()
        # загрузка дизайна
        self.initUI()

    def initUI(self):
        # фиксируем размер окна

        super(Color, self).initUI()

        # подключаем кнопки к функциям
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
            # подключение к БД
            con = sqlite3.connect("lada.db")
            # создание курсора
            cur = con.cursor()

            # выполнение запроса и получение всех результатов
            result = cur.execute(f"""SELECT * FROM Color
                                                    WHERE Model = '{self.mod}' AND Body = '{self.body}'
                                                    AND Complectation = '{self.equip}'""").fetchall()
            con.close()

            super(Color, self).main(result, (3, 4, 5), 'color')
            self.label_2.setText('Цвет Автомобиля')
        else:
            self.db_error()

    def show_window7(self):
        button = QApplication.instance().sender()
        text = button.text().split('\n')
        self.characteristic.append(''.join(text[:-1]))
        self.price.append(int(text[-1].replace(' ', '').replace('от', '')[:-1]))
        self.image = self.image[button]
        self.w = In_total(self.mod, self.body, self.equip, self.price, self.characteristic, self.image)
        self.w.show()
        self.hide()

    def main_window(self):
        # открываем первое окно, закрыв текущее
        self.w = Main_window()
        self.w.show()
        self.hide()

    def back(self):
        # открываем прошлое окно, закрыв текущее
        self.w = Options(self.mod, self.body, self.equip, self.characteristic, self.price)
        self.w.show()
        self.hide()


class In_total(QWidget):
    def __init__(self, *data):
        # получаем список характеристик автомобилий
        self.data = data
        super().__init__()
        # загрузка дизайна
        uic.loadUi("./ui/fwindow.ui", self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Trueconf')
        self.pushButton.clicked.connect(self.main_window)

        self.In_total()

    def In_total(self):
        # вставляем картинку
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

        self.pushButton_2.clicked.connect(self.save)
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
        # открываем первое окно, закрыв текущее
        self.w = Main_window()
        self.w.show()
        self.hide()

    def save(self):
        # открываем диалоговое оно
        filename, ok = QFileDialog.getSaveFileName(self, "Сохранить файл", ".", "(*.txt)")
        # проверяем, что файл сохранили
        # записываем в файл информацию
        if filename:
            f = open(filename, 'w')
            f.write(f"Ваш автомобиль - {self.data[1]}, {price_proc(str(sum(self.data[3])))} руб.")
            f.write("\n")
            f.write(f"\nДвигатель: {self.data[4][0]}")
            f.write(f"\nЦвет: {self.data[4][-1]}, {price_proc(self.data[3][-1])} руб.")
            f.write("\nОпции:")
            for i in range(len(self.data[4][1:-1])):
                f.write(f"\n{i + 1}. {self.data[4][i + 1]}, {price_proc(self.data[3][i + 2])} руб.")
            f.close()


class Settings(QWidget):
    def __init__(self):
        super().__init__()
        # загрузка дизайна
        uic.loadUi("./ui/settings.ui", self)
        self.initUI()

    def initUI(self):
        # фиксируем размеры окна
        self.setFixedSize(700, 500)
        # даём название окну
        self.setWindowTitle('Настройки')
        self.pushButton_3.clicked.connect(self.update)
        self.pushButton_4.clicked.connect(self.back)

    def update(self):
        global timeup
        if time.monotonic() - timeup > 1800:
            w = Load()
            w.show()
            self.hide()
            DBUPDATE.all_update(self.checkBox.isChecked(), self.checkBox_2.isChecked())
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
        # загрузка дизайна
        uic.loadUi("./ui/load.ui", self)
        self.setWindowTitle('Ожидайте окончания загрузки')
        self.setFixedSize(400, 1)


db, brand = None, None
timeup = -1801
compl_inf = ''


def price_proc(price):
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
