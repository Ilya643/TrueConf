import os
import shutil
import time
import unicodedata
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from abc import ABC, abstractmethod
import sqlite3 as sql
from http.client import IncompleteRead

disable_warnings(InsecureRequestWarning)


class Parsing(ABC):

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Referer': 'https://www.lada.ru/configurator',
            'Origin': 'https://www.lada.ru',
            'Connection': 'keep-alive',
        }
        self.proxies = None
        self.session = None
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.last_rel_path = None

    @abstractmethod
    def get_model(self):
        pass

    @abstractmethod
    def get_body(self):
        pass

    def get_complectations(self):
        pass

    @abstractmethod
    def get_engine(self):
        pass

    @abstractmethod
    def get_options(self):
        pass

    @abstractmethod
    def get_color(self):
        pass

    def _normalize_unicode(self, text):
        """Приводит текст к единому стандарту Unicode (NFC)"""
        if not text:
            return ""
        return unicodedata.normalize('NFC', str(text))

    def _normalize_url(self, url):
        if not url:
            return None
        url = str(url).strip()
        if url.startswith('http://') or url.startswith('https://'):
            url = url.replace('https://https://', 'https://').replace('http://http://', 'http://')
            parts = url.split('://')
            if len(parts) > 2:
                url = parts[0] + '://' + parts[-1]
            return url
        if url.startswith('//'):
            return 'https:' + url
        if url.startswith('/'):
            return 'https://static.lada.ru' + url
        return 'https://static.lada.ru/' + url

    def _safe_json_request(self, url, method='GET', timeout=10, expect_dict=True, **kwargs):
        kwargs.setdefault('verify', False)
        kwargs.setdefault('headers', self.headers)
        kwargs.setdefault('proxies', self.proxies)

        try:
            resp = self.session.request(method, url, timeout=timeout, stream=False, **kwargs)
            if resp.status_code >= 400:
                return None
            data = resp.json()
            if expect_dict and not isinstance(data, dict):
                return None
            return data
        except requests.exceptions.Timeout:
            return None
        except requests.exceptions.ConnectionError:
            return None
        except Exception:
            return None

    def makedir(self, name, brand):
        brand_path = os.path.join(self.base_dir, brand)
        if os.path.exists(brand_path):
            shutil.rmtree(brand_path)
        os.makedirs(brand_path, exist_ok=True)
        os.chdir(brand_path)
        os.makedirs(name, exist_ok=True)
        os.chdir(name)

    def get_filei(self, url):
        url = self._normalize_url(url)
        if not url:
            return b''

        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                r = self.session.get(
                    url,
                    headers=self.headers,
                    proxies=self.proxies,
                    verify=False,
                    timeout=20,
                    stream=False
                )
                r.raise_for_status()
                return r.content
            except (requests.exceptions.ChunkedEncodingError,
                    IncompleteRead,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout):
                if attempt < max_attempts - 1:
                    time.sleep(1.5 * (attempt + 1))
                continue
            except Exception:
                break
        return b''

    def get_namei(self, inf):
        # Нормализуем входные данные до создания имени
        folder = self._normalize_unicode(inf[0]).replace(' ', '_').strip()
        safe_name = self._normalize_unicode(inf[1])

        # Очистка от спецсимволов
        safe_name = ''.join(c if c.isalnum() or c in '._- ' else '_' for c in safe_name)
        safe_name = safe_name.strip('_')
        filename = f"{folder}_{safe_name}.png"

        os.makedirs(folder, exist_ok=True)
        abs_path = os.path.join(os.path.abspath(folder), filename)

        # Получаем относительный путь
        rel_path = os.path.relpath(abs_path, self.base_dir)

        # Приводим слеши к одному виду и нормализуем unicode для БД
        # replace('\\', '/') делает путь универсальным для Win и Mac
        self.last_rel_path = self._normalize_unicode(rel_path).replace('\\', '/')

        return abs_path

    def image_save(self, url, inf):
        try:
            abs_name = self.get_namei(inf)
            data = self.get_filei(url)
            if data:
                with open(abs_name, 'wb') as f:
                    f.write(data)
                time.sleep(0.1)
                return self.last_rel_path
            return None
        except Exception:
            return None


class ParsingLada(Parsing):
    BLACKLIST = set()

    def __init__(self, *urls):
        super().__init__()
        if len(urls) < 4:
            raise ValueError("Нужно передать 4 URL для API")
        self.url_m = urls[0]
        self.url_c = urls[1]
        self.url_o = urls[2]
        self.url_color = urls[3]

        self.session = requests.Session()
        retry = Retry(total=2, backoff_factor=0.2, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)

    def return_everything(self, proxy, use_headers):
        if proxy is False or not proxy:
            self.proxies = None
        elif isinstance(proxy, str):
            self.proxies = {'http': proxy, 'https': proxy}
        elif isinstance(proxy, dict):
            self.proxies = proxy

        if use_headers is False:
            self.headers = None

        response_m = None
        for attempt in range(3):
            try:
                resp = self.session.get(self.url_m, headers=self.headers, proxies=self.proxies, verify=False,
                                        timeout=20)
                resp.raise_for_status()
                response_m = resp.json()
                break
            except Exception:
                time.sleep(3)
        if not response_m or not isinstance(response_m, list):
            raise RuntimeError("Не удалось получить данные моделей")

        self.makedir('pictures', 'lada')
        models = self.get_model(response_m)
        bodies, bodies_id = self.get_body(response_m)

        complectations, equipment = {}, {}
        engines_id, modifications_id = {}, {}

        for idx, (body_name, body_id) in enumerate(bodies_id.items(), 1):
            if body_id in self.BLACKLIST:
                continue

            url = self.url_c.replace('*', str(body_id))
            response_c = self._safe_json_request(url, timeout=12, expect_dict=True)
            if not response_c:
                continue

            comps = response_c.get('complectations', [])
            for comp_inf in comps:
                if not isinstance(comp_inf, dict):
                    continue
                result = self.get_complectations(comp_inf, body_name)
                if not result:
                    continue
                c_name, c_data, eng_ids, mod_id = result
                key = f'{body_name}*{c_name}'
                complectations[key] = c_data
                engines_id[key] = eng_ids
                modifications_id[key] = mod_id

            engines_list = response_c.get('engines', [])
            if engines_list and isinstance(engines_list, list):
                equipment.update(self.get_engine(engines_list, engines_id))

            equipment.update(self.get_options(modifications_id))
            time.sleep(0.2)

        colors = self.get_color(modifications_id)

        os.chdir('..')
        os.chdir('..')

        return {
            'brand': 'lada',
            'models': models,
            'bodies': bodies,
            'complectations': complectations,
            'equipment': equipment,
            'colors': colors
        }

    def get_model(self, response_m):
        models = {}
        cars = response_m[0].get('cars', [])[:-1] if len(response_m) > 0 else []
        for car in cars:
            if not isinstance(car, dict):
                continue
            name = car.get('name', 'Unknown')
            price = car.get('price', 0)
            img = car.get('img')
            img_path = self.image_save(img, ('models', name)) if img else None
            models[name] = (price, img_path)
            time.sleep(0.05)
        return models

    def get_body(self, response_m):
        bodies, bodies_id = {}, {}
        for item in response_m[1:-1] if len(response_m) > 2 else []:
            if not isinstance(item, dict):
                continue
            model_title = item.get('title', 'Unknown')
            for car in item.get('cars', []):
                if not isinstance(car, dict):
                    continue
                body_name = f"{model_title}*{car.get('name', 'Unknown')}"
                price = car.get('price', 0)
                img = car.get('image')
                img_path = self.image_save(img, ('bodies', body_name)) if img else None
                bodies[body_name] = (price, img_path)
                if car.get('id'):
                    bodies_id[body_name] = car['id']
                time.sleep(0.05)
        return bodies, bodies_id

    def get_complectations(self, comp_inf, body_id):
        try:
            name = comp_inf.get('title', '').replace("'", '').strip()
            mods = comp_inf.get('modifications', [])
            if not mods or not isinstance(mods, list):
                return None

            engine_ids = []
            for m in mods:
                if not isinstance(m, dict):
                    continue
                eid = m.get('engine_id')
                if eid:
                    engine_ids.append((eid, m.get('price', 0)))

            first_mod = mods[0]
            img = comp_inf.get('image')
            img_path = self.image_save(img, ('complectations', f'{body_id}_{name}')) if img else None

            data = (first_mod.get('price', 0), img_path, first_mod.get('features', []))
            return name, data, engine_ids, first_mod.get('id')
        except Exception:
            return None

    def get_engine(self, engines_list, engines_id):
        result = {}
        for comp_key, id_pairs in engines_id.items():
            for eng in engines_list:
                if not isinstance(eng, dict):
                    continue
                for eng_id, price in id_pairs:
                    if eng.get('id') == eng_id:
                        title = eng.get('title', 'Unknown')
                        img = eng.get('image')
                        img_path = self.image_save(img, ('engines', f'{comp_key}_{title}')) if img else None
                        key = f'{comp_key}*двигатель*{title}'
                        result[key] = (title, price, img_path)
                        time.sleep(0.05)
        return result

    def get_options(self, modifications_id):
        options = {}
        for idx, (comp_key, mod_id) in enumerate(modifications_id.items(), 1):
            if idx % 10 == 0:
                print(f"Опции: {idx}/{len(modifications_id)}")

            url = self.url_o.replace('*', str(mod_id))
            data = self._safe_json_request(url, timeout=8, expect_dict=False)
            if data is None:
                continue

            if isinstance(data, list):
                packages = data
            elif isinstance(data, dict):
                packages = data.get('packages', data.get('options', []))
            else:
                continue

            for opt in packages:
                if not isinstance(opt, dict):
                    continue
                title = opt.get('title', 'Unknown')
                lst = opt.get('list', opt.get('description', []))
                price = opt.get('price', 0)
                img = opt.get('image')
                img_path = self.image_save(img, ('options', f'{comp_key}_{title}')) if img else None
                key = f"{comp_key}*{title}"
                options[key] = (lst, price, img_path)
                time.sleep(0.03)
        return options

    def get_color(self, modifications_id):
        colors = {}
        for idx, (comp_key, mod_id) in enumerate(modifications_id.items(), 1):
            if idx % 10 == 0:
                print(f"Цвета: {idx}/{len(modifications_id)}")

            url = self.url_color.replace('*', str(mod_id))
            data = self._safe_json_request(url, timeout=8, expect_dict=False)
            if data is None:
                continue

            if isinstance(data, list):
                color_list = data
            elif isinstance(data, dict):
                color_list = data.get('colors', data.get('spectrum', []))
            else:
                continue

            for col in color_list:
                if not isinstance(col, dict):
                    continue
                title = col.get('title', 'Unknown')
                price = col.get('price', 0)
                imgs = col.get('images', [])
                img_url = imgs[0] if isinstance(imgs, list) and imgs else (imgs if imgs else None)
                img_path = self.image_save(img_url, ('colors', f'{comp_key}_{title}')) if img_url else None
                colors[f'{comp_key}*{title}'] = (price, img_path)
                time.sleep(0.03)
        return colors


class UpdateDB:

    def __init__(self, data):
        self.data = data
        db_name = f"{data['brand']}.db"

        conn = sql.connect(db_name)
        cursor = conn.cursor()

        self._create_tables(cursor)
        self._fill_data(cursor, data)

        conn.commit()
        cursor.close()
        conn.close()

    def _create_tables(self, cur):
        tables = {
            'MODEL': 'Model TEXT PRIMARY KEY, Price INT, Image TEXT',
            'BODY': 'Model TEXT, Body TEXT, Price INT, Image TEXT, PRIMARY KEY (Model, Body)',
            'COMPLECTATION': 'Model TEXT, Body TEXT, Complectation TEXT, List_options TEXT, Price INT, Image TEXT, PRIMARY KEY (Model, Body, Complectation)',
            'EQUIPMENT': 'Model TEXT, Body TEXT, Complectation TEXT, Option TEXT, Output TEXT, Price INT, Image TEXT, PRIMARY KEY (Model, Body, Complectation, Option)',
            'COLOR': 'Model TEXT, Body TEXT, Complectation TEXT, Color TEXT, Price INT, Image TEXT, PRIMARY KEY (Model, Body, Complectation, Color)',
        }
        for name, schema in tables.items():
            cur.execute(f'CREATE TABLE IF NOT EXISTS {name} ({schema})')

    def _fill_data(self, cur, data):
        cur.execute('DELETE FROM MODEL')
        for name, (price, img) in data.get('models', {}).items():
            # Нормализуем путь перед записью в БД
            img_path = unicodedata.normalize('NFC', img) if img else None
            cur.execute('INSERT INTO MODEL VALUES (?,?,?)', (name, price, img_path))

        cur.execute('DELETE FROM BODY')
        for key, (price, img) in data.get('bodies', {}).items():
            parts = key.split('*')
            if len(parts) >= 2:
                img_path = unicodedata.normalize('NFC', img) if img else None
                cur.execute('INSERT INTO BODY VALUES (?,?,?,?)', (parts[0], parts[1], price, img_path))

        cur.execute('DELETE FROM COMPLECTATION')
        for key, (price, img, opts) in data.get('complectations', {}).items():
            parts = key.split('*')
            if len(parts) >= 3:
                opts_str = '*'.join(opts) if isinstance(opts, list) else opts
                img_path = unicodedata.normalize('NFC', img) if img else None
                cur.execute('INSERT INTO COMPLECTATION VALUES (?,?,?,?,?,?)',
                            (parts[0], parts[1], parts[2], opts_str, price, img_path))

        cur.execute('DELETE FROM EQUIPMENT')
        for key, (title, price, img) in data.get('equipment', {}).items():
            parts = key.split('*')
            if len(parts) >= 4:
                option = parts[3]
                output = '*'.join(title) if isinstance(title, list) else title
                img_path = unicodedata.normalize('NFC', img) if img else None
                cur.execute('INSERT INTO EQUIPMENT VALUES (?,?,?,?,?,?,?)',
                            (parts[0], parts[1], parts[2], option, output, price, img_path))

        cur.execute('DELETE FROM COLOR')
        for key, (price, img) in data.get('colors', {}).items():
            parts = key.split('*')
            if len(parts) >= 4:
                img_path = unicodedata.normalize('NFC', img) if img else None
                cur.execute('INSERT INTO COLOR VALUES (?,?,?,?,?,?)',
                            (parts[0], parts[1], parts[2], parts[3], price, img_path))


def all_update(proxy=False, use_headers=True):
    parser = ParsingLada(
        'https://www.lada.ru/api-v1/combinations/model-header-range',
        'https://www.lada.ru/api-v1/configurators/complectations/*/base-id/938134/city-id',
        'https://www.lada.ru/api-v1/configurators/packages/*/kompl-id',
        'https://www.lada.ru/api-v1/configurators/spectrum/*/kompl-id'
    )
    data = parser.return_everything(proxy, use_headers)
    UpdateDB(data)


brands = {'LADA': 'lada.db'}

if __name__ == '__main__':
    all_update()
