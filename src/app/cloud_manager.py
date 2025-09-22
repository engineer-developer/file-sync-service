from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar

import requests
from requests import Response

from config import settings
from logger import logger_app


@dataclass
class CloudDirManager:
    """Менеджер облачного хранилища"""

    headers: ClassVar[dict] = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    api_url: ClassVar[str] = "https://cloud-api.yandex.net/v1/disk/"

    token: str
    cloud_dir: str

    def __post_init__(self):
        """Инициализация токена"""
        self.headers["Authorization"] = f"OAuth {self.token}"

    def get_dir_info(self) -> dict:
        """Получаем информацию о файлах в папке облачного хранилища"""
        url = f"{self.api_url}resources"
        params = {
            "path": self.cloud_dir,
            "fields": "_embedded.items.name,_embedded.items.modified",
            "limit": 10**6,
        }
        response: Response = requests.get(
            url=url,
            params=params,
            headers=self.headers,
        )
        dir_info = response.json()
        return dir_info

    def get_files_stats(self) -> dict[str, dict[str, datetime]]:
        """
        Получаем информацию о дате и времени изменения файлов
        :return: stats (dict), где:
        ключ словаря - имя файла, значение словаря - {"modified": datetime}
        """
        stats = dict()
        source_data = self.get_dir_info()
        _embedded_data = source_data.get("_embedded")
        items = _embedded_data.get("items")
        for item in items:
            name = item.get("name")
            modified = item.get("modified")
            dt_modified = datetime.fromisoformat(modified)
            stats[name] = dict(modified=dt_modified)
        return stats


cloud_manager = CloudDirManager(
    token=settings.auth_token,
    cloud_dir=settings.cloud_dir,
)

cloud_manager.get_files_stats()
