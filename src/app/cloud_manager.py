from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar
from datetime import datetime
from pathlib import Path

import logger_module
import requests


class CloudDirManagerInterface(ABC):
    """
    Интерфейс менеджера облачного хранилища
    """

    token: str
    cloud_dir: str

    @abstractmethod
    def get_info(self) -> dict[str, dict[str, datetime]]:
        """Метод получения информации о хранящихся в удалённом хранилище файлах"""
        pass

    @abstractmethod
    def load(self, file: Path) -> None:
        """Метод загрузки файла в хранилище"""
        pass

    @abstractmethod
    def reload(self, file: Path) -> None:
        """Метод перезаписи файла в хранилище"""
        pass

    @abstractmethod
    def delete(self, file: Path) -> None:
        """Метод удаления файла из хранилища"""
        pass


@dataclass
class CloudDirManager(CloudDirManagerInterface):
    """Менеджер облачного хранилища Яндекс-Диск"""

    headers: ClassVar[dict] = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    api_url: ClassVar[str] = "https://cloud-api.yandex.net/v1/disk"
    resource_url: ClassVar[str] = f"{api_url}/resources"
    resource_upload_url: ClassVar[str] = f"{resource_url}/upload"

    token: str
    cloud_dir: str
    logger_app: logger_module.logger

    def __post_init__(self) -> None:
        """Добавление в заголовки OAuth-токена"""
        self.headers["Authorization"] = f"OAuth {self.token}"

    def fetch_info_from_cloud(self, limit: int = 10**6) -> dict | None:
        """Извлекаем информацию с Яндекс-Диск через API"""
        params = {
            "path": self.cloud_dir,
            "fields": "_embedded.items.name,_embedded.items.modified",
            "limit": limit,
        }
        try:
            response: requests.Response = requests.get(
                url=self.resource_url,
                params=params,
                headers=self.headers,
                timeout=5,
            )

            if response.status_code == 200:
                info: dict = response.json()
                return info
            else:
                self.logger_app.error("Не удалось извлечь данные из облака")

        except requests.exceptions.ConnectTimeout:
            self.logger_app.error("Ошибка: произошла ошибка подключения.")

    @staticmethod
    def convert_data_to_specific_format(
        input_data: dict,
    ) -> dict[str, dict[str, datetime]]:
        """
        Получаем информацию о файлах и структурируем её.

        :param input_data: Информация о файлах из облака
        :return: stats - сведения о файлах, где ключ словаря - это имя файла, значение словаря - словарь: {"modified": datetime}
        :rtype: dict[str, dict[str, datetime]]
        """
        stats = dict()
        embedded_data = input_data.get("_embedded")
        items = embedded_data.get("items")

        for item in items:
            name = item.get("name")
            modified = item.get("modified")
            dt_modified = datetime.fromisoformat(modified)
            stats[name] = dict(modified=dt_modified)

        return stats

    def get_info(self) -> dict[str, dict[str, datetime]]:
        """
        Получаем информацию о файлах в папке облачного хранилища
        :return: info
        """
        info_from_cloud = self.fetch_info_from_cloud()
        info = self.convert_data_to_specific_format(info_from_cloud)
        return info

    def get_upload_url(self, file: Path, overwrite: bool) -> str | None:
        """
        Метод получения ссылки для загрузки файла в облако.
        :param file: Загружаемый или обновляемый файл
        :param overwrite: Параметр перезаписи файла
        :return: url | None
        """
        params = {
            "path": f"/{self.cloud_dir}/{file.name}",
            "overwrite": overwrite,
        }
        try:
            response: requests.Response = requests.get(
                url=self.resource_upload_url,
                params=params,
                headers=self.headers,
                timeout=5,
            )
            if response.status_code == 200:
                url = response.json().get("href")
                return url

        except requests.exceptions.ConnectTimeout:
            self.logger_app.error("Ошибка: произошла ошибка подключения.")
        except requests.exceptions.RequestException as exc:
            self.logger_app.error("Ошибка: {}", exc)

    def produce_load_result_message(
        self, response: requests.Response, file: Path, overwrite: bool
    ) -> None:
        """
        Выводим сообщение о результатах загрузки файла в облако.
        :param response: Объект ответ от сервера
        :param file: Загружаемый или обновляемый файл
        :param overwrite: Параметр перезаписи файла
        :return: None
        """
        if response.status_code == 201:
            file_copy_method: str = "записан" if not overwrite else "перезаписан"
            self.logger_app.info("Файл '{}' успешно {}.", file.name, file_copy_method)
        else:
            self.logger_app.error("Не удалось загрузить файл '{}'.", file.name)

    def load(self, file: Path, overwrite=False) -> None:
        """
        Метод загрузки файла в облачное хранилище.
        :param file: Загружаемый файл
        :param overwrite: Параметр перезаписи файла
        :return: None
        """
        upload_url = self.get_upload_url(file=file, overwrite=overwrite)

        if upload_url:
            files = {"file": (file.name, open(file, "rb"), "application/octet-stream")}
            self.headers["Content-Type"] = "application/octet-stream"
            try:
                response: requests.Response = requests.put(
                    url=upload_url,
                    files=files,
                    headers=self.headers,
                    timeout=5,
                )
                self.produce_load_result_message(
                    response=response, file=file, overwrite=overwrite
                )

            except requests.exceptions.ConnectTimeout:
                self.logger_app.error("Ошибка: произошла ошибка подключения.")
            except requests.exceptions.RequestException as exc:
                self.logger_app.error("Ошибка: {}", exc)

        else:
            self.logger_app.error("Не удалось получить ссылку для загрузки файла")

    def reload(self, file) -> None:
        """
        Метод обновления файла в облачном хранилище.\
        Использует метод загрузки файлов в облако с параметром overwrite=True.
        :param file: Обновляемый файл
        :return: None
        """
        return self.load(file, overwrite=True)

    def delete(self, file: Path) -> None:
        """
        Метод удаления файла из облачного хранилища.
        :param file: Удаляемый файл
        :return: None
        """
        params = {"path": f"/{self.cloud_dir}/{file.name}"}
        try:
            response: requests.Response = requests.delete(
                url=self.resource_url,
                params=params,
                headers=self.headers,
                timeout=5,
            )
            if response.status_code == 204:
                self.logger_app.info(
                    "Файл '{}' удален из облачного хранилища.", file.name
                )
            else:
                self.logger_app.error("Не удалось удалить файл '{}'", file.name)

        except requests.exceptions.ConnectTimeout:
            self.logger_app.error("Ошибка: произошла ошибка подключения.")
        except requests.exceptions.RequestException as exc:
            self.logger_app.error("Ошибка: {}", exc)
