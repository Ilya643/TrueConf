"""
Базовый класс парсера: HTTP-запросы и работа с файлами.

Содержит абстрактный класс ``Parsing`` - общий интерфейс и
вспомогательные методы для всех конкретных парсеров брендов.
"""

import os
import shutil
import time
import unicodedata
from abc import ABC, abstractmethod
from http.client import IncompleteRead

import requests
from requests.adapters import HTTPAdapter
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from urllib3.util.retry import Retry

disable_warnings(InsecureRequestWarning)


class Parsing(ABC):
    """Абстрактный базовый класс для всех парсеров автобрендов.

    Подклассы обязаны реализовать:
    ``get_model``, ``get_body``, ``get_engine``, ``get_options``, ``get_color``.
    """

    def __init__(self) -> None:
        """Инициализирует HTTP-заголовки и состояние парсера."""
        self.headers: dict = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
            "Referer": "https://www.lada.ru/configurator",
            "Origin": "https://www.lada.ru",
            "Connection": "keep-alive",
        }
        self.proxies: dict | None = None
        self.session: requests.Session | None = None
        self.base_dir: str = os.path.abspath(os.path.dirname(__file__))
        self.last_rel_path: str | None = None

    # Заглушки
    @abstractmethod
    def get_model(self, *args, **kwargs) -> dict:
        """Возвращает словарь моделей {название: (цена, путь_к_фото)}."""

    @abstractmethod
    def get_body(self, *args, **kwargs) -> tuple:
        """Возвращает кортеж (dict тел, dict id_тел)."""

    @abstractmethod
    def get_engine(self, *args, **kwargs) -> dict:
        """Возвращает словарь двигателей."""

    @abstractmethod
    def get_options(self, *args, **kwargs) -> dict:
        """Возвращает словарь дополнительных опций."""

    @abstractmethod
    def get_color(self, *args, **kwargs) -> dict:
        """Возвращает словарь цветов."""

    def _normalize_unicode(self, text: str) -> str:
        """Приводит строку к каноническому Unicode NFC.

        Args:
            text: Исходная строка.

        Returns:
            Нормализованная строка или «» при None.
        """
        if not text:
            return ""
        return unicodedata.normalize("NFC", str(text))

    def _normalize_url(self, url: str | None) -> str | None:
        """Приводит URL к абсолютному виду с протоколом https.

        Args:
            url: Исходный URL (может быть относительным).

        Returns:
            Абсолютный URL или None.
        """
        if not url:
            return None
        url = str(url).strip()
        if url.startswith(("http://", "https://")):
            url = url.replace("https://https://", "https://")
            url = url.replace("http://http://", "http://")
            parts = url.split("://")
            if len(parts) > 2:
                url = parts[0] + "://" + parts[-1]
            return url
        if url.startswith("//"):
            return "https:" + url
        if url.startswith("/"):
            return "https://static.lada.ru" + url
        return "https://static.lada.ru/" + url

    def _safe_json_request(
        self, url: str, method: str = "GET",
        timeout: int = 10, expect_dict: bool = True, **kwargs
    ) -> dict | list | None:
        """Выполняет HTTP-запрос и возвращает JSON или None при ошибке.

        Args:
            url: Адрес API-эндпоинта.
            method: HTTP-метод.
            timeout: Таймаут в секундах.
            expect_dict: Если True, возвращает None при получении списка.
            **kwargs: Дополнительные аргументы для requests.

        Returns:
            dict, list или None.
        """
        kwargs.setdefault("verify", False)
        kwargs.setdefault("headers", self.headers)
        kwargs.setdefault("proxies", self.proxies)
        try:
            resp = self.session.request(method, url, timeout=timeout, stream=False, **kwargs)
            if resp.status_code >= 400:
                return None
            data = resp.json()
            if expect_dict and not isinstance(data, dict):
                return None
            return data
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            return None
        except Exception:
            return None

    def makedir(self, name: str, brand: str) -> None:
        """Создаёт/очищает директорию для изображений бренда.

        Args:
            name: Имя поддиректории.
            brand: Название бренда.
        """
        brand_path = os.path.join(self.base_dir, brand)
        if os.path.exists(brand_path):
            shutil.rmtree(brand_path)
        os.makedirs(brand_path, exist_ok=True)
        os.chdir(brand_path)
        os.makedirs(name, exist_ok=True)
        os.chdir(name)

    def get_filei(self, url: str) -> bytes:
        """Скачивает файл по URL (3 попытки при сбоях).

        Args:
            url: URL ресурса.

        Returns:
            Байтовое содержимое файла или b'' при ошибке.
        """
        url = self._normalize_url(url)
        if not url:
            return b""
        for attempt in range(3):
            try:
                resp = self.session.get(
                    url, headers=self.headers, proxies=self.proxies,
                    verify=False, timeout=20, stream=False,
                )
                resp.raise_for_status()
                return resp.content
            except (requests.exceptions.ChunkedEncodingError, IncompleteRead,
                    requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
            except Exception:
                break
        return b""

    def get_namei(self, inf: tuple) -> str:
        """Формирует абсолютный путь для сохранения изображения.

        Записывает относительный путь в ``self.last_rel_path``.

        Args:
            inf: Кортеж (категория, название).

        Returns:
            Абсолютный путь к файлу.
        """
        folder = self._normalize_unicode(inf[0]).replace(" ", "_").strip()
        safe_name = self._normalize_unicode(inf[1])
        safe_name = "".join(c if c.isalnum() or c in "._- " else "_" for c in safe_name)
        safe_name = safe_name.strip("_")
        filename = f"{folder}_{safe_name}.png"
        os.makedirs(folder, exist_ok=True)
        abs_path = os.path.join(os.path.abspath(folder), filename)
        rel_path = os.path.relpath(abs_path, self.base_dir)
        self.last_rel_path = self._normalize_unicode(rel_path).replace("\\", "/")
        return abs_path

    def image_save(self, url: str, inf: tuple) -> str | None:
        """Скачивает изображение и сохраняет его на диск.

        Args:
            url: URL изображения.
            inf: Кортеж (категория, название).

        Returns:
            Относительный путь к файлу или None при ошибке.
        """
        try:
            abs_name = self.get_namei(inf)
            data = self.get_filei(url)
            if data:
                with open(abs_name, "wb") as f:
                    f.write(data)
                time.sleep(0.1)
                return self.last_rel_path
        except Exception:
            pass
        return None


def make_session() -> requests.Session:
    """Создаёт requests.Session с авторетраями на ошибки сервера.

    Returns:
        Настроенный объект Session.
    """
    session = requests.Session()
    retry = Retry(total=2, backoff_factor=0.2, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session
