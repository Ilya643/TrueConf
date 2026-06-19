"""
Фасад обратной совместимости для обновления базы данных.

Делегирует работу модулям пакета ``app``::

    app.lada_parser  - парсер API lada.ru и обновление SQLite.
    app.db_manager   - создание и заполнение таблиц БД.

Прямой запуск::

    python DBUPDATE.py

инициализирует файл ``lada.db`` и скачивает изображения.
"""

from app.lada_parser import ParsingLada
from app.db_manager import UpdateDB

#: Доступные бренды и соответствующие файлы баз данных
brands: dict = {"LADA": "lada.db"}


def all_update(proxy=False, use_headers: bool = True) -> None:
    """Запускает полное обновление данных LADA.

    Args:
        proxy: Настройки прокси (False - без прокси, str или dict).
        use_headers: Отправлять ли HTTP-заголовки браузера.
    """
    parser = ParsingLada(
        url_models="https://www.lada.ru/api-v1/combinations/model-header-range",
        url_complect=(
            "https://www.lada.ru/api-v1/configurators/"
            "complectations/*/base-id/938134/city-id"
        ),
        url_options="https://www.lada.ru/api-v1/configurators/packages/*/kompl-id",
        url_color="https://www.lada.ru/api-v1/configurators/spectrum/*/kompl-id",
    )
    data = parser.return_everything(proxy, use_headers)
    UpdateDB(data)


if __name__ == "__main__":
    all_update()
