from dataclasses import dataclass
from typing import ClassVar

import requests
from requests import Response

from config import settings
from logger import logger_app


@dataclass
class CloudManager:
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

    def get_dir_info(self) -> Response:
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
        logger_app.debug("Сведения из облачного хранилища: {}", response.json())
        return response


cloud_manager = CloudManager(
    token=settings.auth_token,
    cloud_dir=settings.cloud_dir,
)

cloud_manager.get_dir_info()
