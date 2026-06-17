"""
Пакет ``app`` — основная логика приложения LADA Configurator.

Структура пакета
----------------
utils.py
    Глобальное состояние сессии (db, brand, timeup, compl_inf)
    и вспомогательная функция ``price_proc``.

base_window.py
    Базовый класс ``Window`` с общей логикой отображения карточек
    и навигации.

main_window.py
    ``MainWindow`` — главное меню.
    ``Settings`` — окно обновления базы данных.
    ``Load`` — заглушка ожидания.

steps.py
    Шаги конфигуратора:
    ``Model`` → ``Body`` → ``Complectation`` → ``Engine``
    → ``Options`` → ``Color``.

summary.py
    ``InTotal`` — итоговое окно с ценой и детализацией.
    ``AnalogSearch`` — поиск аналогов на Auto.ru.

dealers.py
    ``DealersMap`` — карта официальных дилеров LADA.
"""
