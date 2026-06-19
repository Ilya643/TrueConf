"""
Точка входа приложения LADA Configurator.

Запускает Qt-приложение и открывает главное меню.

Использование::

    python Trueconf.py

или (после компиляции cx_Freeze)::

    build\\exe.win-amd64-3.11\\Trueconf.exe
"""

import sys

import PyQt5.QtWidgets

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from app.main_window import MainWindow


def main() -> int:
    """Инициализирует QApplication и запускает главное окно.

    Returns:
        Код завершения процесса (0 - успех, ненулевой - ошибка).
    """
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
