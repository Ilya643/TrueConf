"""
Точка входа приложения LADA Configurator.

Запускает Qt-приложение и открывает главное меню.

Использование::

    python Trueconf.py

или (после компиляции cx_Freeze)::

    build\\exe.win-amd64-3.11\\Trueconf.exe
"""

import sys

from PyQt5.QtWidgets import QApplication

from app.main_window import MainWindow


def main() -> int:
    """Инициализирует QApplication и запускает главное окно.

    Returns:
        Код завершения процесса (0 — успех, ненулевой — ошибка).
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
