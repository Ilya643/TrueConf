"""
Парсер API lada.ru.

Содержит ``ParsingLada`` — конкретную реализацию парсера,
которая собирает модели, кузова, комплектации, двигатели,
опции и цвета с официального сайта LADA.
"""

import os
import time

from app.parsing import Parsing, make_session


class ParsingLada(Parsing):
    """Парсер официального API lada.ru.

    Args:
        url_models: URL списка моделей.
        url_complect: URL комплектаций (содержит «*» вместо ID кузова).
        url_options: URL опций (содержит «*» вместо ID модификации).
        url_color: URL цветов (содержит «*» вместо ID модификации).
    """

    BLACKLIST: set = set()

    def __init__(self, url_models: str, url_complect: str,
                 url_options: str, url_color: str) -> None:
        """Инициализирует парсер и HTTP-сессию с авторетраями."""
        super().__init__()
        self.url_m = url_models
        self.url_c = url_complect
        self.url_o = url_options
        self.url_color = url_color
        self.session = make_session()

    def return_everything(self, proxy, use_headers: bool) -> dict:
        """Запускает полный цикл парсинга LADA.

        Args:
            proxy: Настройки прокси (False/None, str или dict).
            use_headers: Использовать ли заголовки браузера.

        Returns:
            Словарь с ключами brand, models, bodies,
            complectations, equipment, colors.

        Raises:
            RuntimeError: Если список моделей недоступен.
        """
        self._apply_proxy(proxy, use_headers)
        response_m = self._fetch_models()
        self.makedir("pictures", "lada")

        models = self.get_model(response_m)
        bodies, bodies_id = self.get_body(response_m)
        complectations, equipment, engines_id, mods_id = {}, {}, {}, {}

        for body_name, body_id in bodies_id.items():
            if body_id in self.BLACKLIST:
                continue
            self._parse_body(body_name, body_id, complectations,
                             equipment, engines_id, mods_id)
            time.sleep(0.2)

        colors = self.get_color(mods_id)
        os.chdir("..")
        os.chdir("..")

        return {"brand": "lada", "models": models, "bodies": bodies,
                "complectations": complectations, "equipment": equipment, "colors": colors}

    def _apply_proxy(self, proxy, use_headers: bool) -> None:
        """Устанавливает прокси и флаг заголовков.

        Args:
            proxy: Настройки прокси.
            use_headers: Если False, отключает заголовки.
        """
        if not proxy:
            self.proxies = None
        elif isinstance(proxy, str):
            self.proxies = {"http": proxy, "https": proxy}
        elif isinstance(proxy, dict):
            self.proxies = proxy
        if use_headers is False:
            self.headers = None

    def _fetch_models(self) -> list:
        """Загружает список моделей (3 попытки).

        Returns:
            JSON-список моделей.

        Raises:
            RuntimeError: При неудаче всех попыток.
        """
        for _ in range(3):
            try:
                resp = self.session.get(self.url_m, headers=self.headers,
                                        proxies=self.proxies, verify=False, timeout=20)
                resp.raise_for_status()
                data = resp.json()
                if isinstance(data, list):
                    return data
            except Exception:
                time.sleep(3)
        raise RuntimeError("Не удалось получить данные моделей LADA")

    def _parse_body(self, body_name: str, body_id: int, complectations: dict,
                    equipment: dict, engines_id: dict, mods_id: dict) -> None:
        """Парсит комплектации, двигатели и опции одного кузова.

        Args:
            body_name: Ключ кузова вида «Модель*Кузов».
            body_id: ID кузова в API.
            complectations: Словарь для записи комплектаций.
            equipment: Словарь для записи оборудования.
            engines_id: Словарь для ID двигателей.
            mods_id: Словарь для ID модификаций.
        """
        url = self.url_c.replace("*", str(body_id))
        resp = self._safe_json_request(url, timeout=12, expect_dict=True)
        if not resp:
            return
        for comp in resp.get("complectations", []):
            if not isinstance(comp, dict):
                continue
            res = self.get_complectations(comp, body_name)
            if not res:
                continue
            c_name, c_data, eng_ids, mod_id = res
            key = f"{body_name}*{c_name}"
            complectations[key] = c_data
            engines_id[key] = eng_ids
            mods_id[key] = mod_id
        engines = resp.get("engines", [])
        if engines:
            equipment.update(self.get_engine(engines, engines_id))
        equipment.update(self.get_options(mods_id))

    def get_model(self, response_m: list) -> dict:
        """Парсит модели и скачивает превью.

        Args:
            response_m: JSON-список от API.

        Returns:
            {название: (цена, путь_фото)}.
        """
        models = {}
        for car in (response_m[0].get("cars", [])[:-1] if response_m else []):
            if not isinstance(car, dict):
                continue
            name = car.get("name", "Unknown")
            img = car.get("img")
            models[name] = (car.get("price", 0),
                            self.image_save(img, ("models", name)) if img else None)
            time.sleep(0.05)
        return models

    def get_body(self, response_m: list) -> tuple:
        """Парсит кузова для каждой модели.

        Args:
            response_m: JSON-список от API.

        Returns:
            Кортеж (dict тел, dict id_тел).
        """
        bodies, bodies_id = {}, {}
        for item in (response_m[1:-1] if len(response_m) > 2 else []):
            if not isinstance(item, dict):
                continue
            model_title = item.get("title", "Unknown")
            for car in item.get("cars", []):
                if not isinstance(car, dict):
                    continue
                key = f"{model_title}*{car.get('name', 'Unknown')}"
                img = car.get("image")
                bodies[key] = (car.get("price", 0),
                               self.image_save(img, ("bodies", key)) if img else None)
                if car.get("id"):
                    bodies_id[key] = car["id"]
                time.sleep(0.05)
        return bodies, bodies_id

    def get_complectations(self, comp: dict, body_id: str) -> tuple | None:
        """Парсит одну комплектацию кузова.

        Args:
            comp: Данные комплектации из API.
            body_id: Ключ кузова.

        Returns:
            (название, данные, id_двиг, id_мод) или None.
        """
        try:
            name = comp.get("title", "").replace("'", "").strip()
            mods = comp.get("modifications", [])
            if not mods:
                return None
            engine_ids = [(m.get("engine_id"), m.get("price", 0))
                          for m in mods if isinstance(m, dict) and m.get("engine_id")]
            first = mods[0]
            img = comp.get("image")
            img_path = self.image_save(img, ("complectations", f"{body_id}_{name}")) if img else None
            return name, (first.get("price", 0), img_path, first.get("features", [])), engine_ids, first.get("id")
        except Exception:
            return None

    def get_engine(self, engines: list, engines_id: dict) -> dict:
        """Сопоставляет ID двигателей с данными.

        Args:
            engines: Список двигателей из API.
            engines_id: {ключ_компл: [(id, цена)]}.

        Returns:
            {ключ: (название, цена, путь_фото)}.
        """
        result = {}
        for key, id_pairs in engines_id.items():
            for eng in engines:
                if not isinstance(eng, dict):
                    continue
                for eid, price in id_pairs:
                    if eng.get("id") == eid:
                        title = eng.get("title", "Unknown")
                        img = eng.get("image")
                        img_path = self.image_save(img, ("engines", f"{key}_{title}")) if img else None
                        result[f"{key}*двигатель*{title}"] = (title, price, img_path)
                        time.sleep(0.05)
        return result

    def get_options(self, mods_id: dict) -> dict:
        """Скачивает дополнительные опции для всех модификаций.

        Args:
            mods_id: {ключ_компл: id_мод}.

        Returns:
            {ключ: (описание, цена, путь_фото)}.
        """
        options = {}
        total = len(mods_id)
        for idx, (key, mod_id) in enumerate(mods_id.items(), 1):
            if idx % 10 == 0:
                print(f"Опции: {idx}/{total}")
            data = self._safe_json_request(self.url_o.replace("*", str(mod_id)), timeout=8, expect_dict=False)
            if data is None:
                continue
            packages = data if isinstance(data, list) else data.get("packages", data.get("options", []))
            for opt in packages:
                if not isinstance(opt, dict):
                    continue
                title = opt.get("title", "Unknown")
                img = opt.get("image")
                img_path = self.image_save(img, ("options", f"{key}_{title}")) if img else None
                options[f"{key}*{title}"] = (opt.get("list", []), opt.get("price", 0), img_path)
                time.sleep(0.03)
        return options

    def get_color(self, mods_id: dict) -> dict:
        """Скачивает цвета для всех модификаций.

        Args:
            mods_id: {ключ_компл: id_мод}.

        Returns:
            {ключ: (цена, путь_фото)}.
        """
        colors = {}
        total = len(mods_id)
        for idx, (key, mod_id) in enumerate(mods_id.items(), 1):
            if idx % 10 == 0:
                print(f"Цвета: {idx}/{total}")
            data = self._safe_json_request(self.url_color.replace("*", str(mod_id)), timeout=8, expect_dict=False)
            if data is None:
                continue
            col_list = data if isinstance(data, list) else data.get("colors", data.get("spectrum", []))
            for col in col_list:
                if not isinstance(col, dict):
                    continue
                title = col.get("title", "Unknown")
                imgs = col.get("images", [])
                img_url = imgs[0] if isinstance(imgs, list) and imgs else (imgs or None)
                img_path = self.image_save(img_url, ("colors", f"{key}_{title}")) if img_url else None
                colors[f"{key}*{title}"] = (col.get("price", 0), img_path)
                time.sleep(0.03)
        return colors
