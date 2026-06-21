"""
Менеджер базы данных SQLite.

Содержит класс ``UpdateDB`` для создания и заполнения таблиц базы
данных по данным, возвращённым парсером.

Схема БД:
    * MODEL         - список моделей с базовыми ценами и фото.
    * BODY          - кузова для каждой модели.
    * COMPLECTATION - комплектации с описанием особенностей.
    * EQUIPMENT     - двигатели и дополнительные опции.
    * COLOR         - доступные цвета для каждой комплектации.
"""

import unicodedata
import sqlite3 as sql


class UpdateDB:
    """Создаёт/перезаписывает SQLite-базу данных по данным парсера.

    Args:
        data: Словарь от ``ParsingLada.return_everything`` с ключами:
              ``brand``, ``models``, ``bodies``, ``complectations``,
              ``equipment``, ``colors``.
    """

    def __init__(self, data: dict) -> None:
        """Открывает соединение, создаёт таблицы и заполняет их."""
        self.data = data
        db_name = f"{data['brand']}.db"
        with sql.connect(db_name) as conn:
            cur = conn.cursor()
            self._create_tables(cur)
            self._fill_data(cur, data)
            conn.commit()


    # Создание схемы
    def _create_tables(self, cur: sql.Cursor) -> None:
        """Создаёт таблицы БД (если не существуют).

        Args:
            cur: Курсор открытого соединения SQLite.
        """
        schemas = {
            "MODEL": "Model TEXT PRIMARY KEY, Price INT, Image TEXT",
            "BODY": (
                "Model TEXT, Body TEXT, Price INT, Image TEXT, "
                "PRIMARY KEY (Model, Body)"
            ),
            "COMPLECTATION": (
                "Model TEXT, Body TEXT, Complectation TEXT, "
                "List_options TEXT, Price INT, Image TEXT, "
                "PRIMARY KEY (Model, Body, Complectation)"
            ),
            "EQUIPMENT": (
                "Model TEXT, Body TEXT, Complectation TEXT, "
                "Option TEXT, Output TEXT, Price INT, Image TEXT, "
                "PRIMARY KEY (Model, Body, Complectation, Option)"
            ),
            "COLOR": (
                "Model TEXT, Body TEXT, Complectation TEXT, "
                "Color TEXT, Price INT, Image TEXT, "
                "PRIMARY KEY (Model, Body, Complectation, Color)"
            ),
        }
        for name, schema in schemas.items():
            cur.execute(f"CREATE TABLE IF NOT EXISTS {name} ({schema})")


    # Заполнение данными
    def _fill_data(self, cur: sql.Cursor, data: dict) -> None:
        """Заполняет все таблицы (полная перезапись).

        Args:
            cur: Курсор SQLite.
            data: Агрегированные данные парсера.
        """
        self._fill_models(cur, data.get("models", {}))
        self._fill_bodies(cur, data.get("bodies", {}))
        self._fill_complectations(cur, data.get("complectations", {}))
        self._fill_equipment(cur, data.get("equipment", {}))
        self._fill_colors(cur, data.get("colors", {}))

    @staticmethod
    def _norm(text: str | None) -> str | None:
        """Нормализует путь к изображению (Unicode NFC).

        Args:
            text: Исходная строка или None.

        Returns:
            Нормализованная строка или None.
        """
        return unicodedata.normalize("NFC", text) if text else None

    def _fill_models(self, cur: sql.Cursor, models: dict) -> None:
        """Перезаписывает таблицу MODEL.

        Args:
            cur: Курсор SQLite.
            models: {название: (цена, путь_фото)}.
        """
        cur.execute("DELETE FROM MODEL")
        for name, (price, img) in models.items():
            cur.execute("INSERT INTO MODEL VALUES (?,?,?)", (name, price, self._norm(img)))

    def _fill_bodies(self, cur: sql.Cursor, bodies: dict) -> None:
        """Перезаписывает таблицу BODY.

        Args:
            cur: Курсор SQLite.
            bodies: {«Модель*Кузов»: (цена, путь_фото)}.
        """
        cur.execute("DELETE FROM BODY")
        for key, (price, img) in bodies.items():
            parts = key.split("*")
            if len(parts) >= 2:
                cur.execute("INSERT INTO BODY VALUES (?,?,?,?)",
                            (parts[0], parts[1], price, self._norm(img)))

    def _fill_complectations(self, cur: sql.Cursor, complectations: dict) -> None:
        """Перезаписывает таблицу COMPLECTATION.

        Args:
            cur: Курсор SQLite.
            complectations: {«Мод*Куз*Компл»: (цена, фото, опции)}.
        """
        cur.execute("DELETE FROM COMPLECTATION")
        for key, (price, img, opts) in complectations.items():
            parts = key.split("*")
            if len(parts) >= 3:
                opts_str = "*".join(opts) if isinstance(opts, list) else opts
                cur.execute("INSERT INTO COMPLECTATION VALUES (?,?,?,?,?,?)",
                            (parts[0], parts[1], parts[2], opts_str, price, self._norm(img)))

    def _fill_equipment(self, cur: sql.Cursor, equipment: dict) -> None:
        """Перезаписывает таблицу EQUIPMENT (двигатели + опции).

        Args:
            cur: Курсор SQLite.
            equipment: {«Мод*Куз*Компл*Опция»: (заголовок, цена, фото)}.
        """
        seen = set()  # Отслеживаем уже вставленные ключи
        cur.execute("DELETE FROM EQUIPMENT")
        for key, (title, price, img) in equipment.items():
            parts = key.split("*")
            if len(parts) >= 4:
                # Уникальный ключ для проверки дубликатов
                unique_key = (parts[0], parts[1], parts[2], parts[3])
                if unique_key in seen:
                    continue  # Пропускаем дубликат
                seen.add(unique_key)
                output = "*".join(title) if isinstance(title, list) else title
                cur.execute("INSERT INTO EQUIPMENT VALUES (?,?,?,?,?,?,?)",
                            (parts[0], parts[1], parts[2], parts[3], output, price, self._norm(img)))

    def _fill_colors(self, cur: sql.Cursor, colors: dict) -> None:
        """Перезаписывает таблицу COLOR.

        Args:
            cur: Курсор SQLite.
            colors: {«Мод*Куз*Компл*Цвет»: (цена, путь_фото)}.
        """
        cur.execute("DELETE FROM COLOR")
        for key, (price, img) in colors.items():
            parts = key.split("*")
            if len(parts) >= 4:
                cur.execute("INSERT INTO COLOR VALUES (?,?,?,?,?,?)",
                            (parts[0], parts[1], parts[2], parts[3], price, self._norm(img)))
