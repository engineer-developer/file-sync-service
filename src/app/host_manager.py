from os import stat_result
from abc import ABC, abstractmethod

from datetime import datetime, UTC
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass
class HostDirManagerInterface(ABC):
    """
    Интерфейс менеджера папки на хосте
    """

    host_dir: Path

    @abstractmethod
    def get_info(self) -> dict[str, dict[str, datetime]]:
        """Метод получения информации о хранящихся на хосте файлах"""
        pass


@dataclass
class HostFile:
    """Класс файла на хосте"""

    file: Path

    def get_file_stat(self) -> stat_result:
        """Получаем информацию о файле"""
        stat = self.file.stat()
        return stat

    def get_modification_timestamp(self) -> int:
        """Получаем timestamp модификации файла"""
        timestamp = int(self.get_file_stat().st_mtime)
        return timestamp

    def get_modification_datetime(self) -> datetime:
        """Получаем дату и время модификации файла"""
        mod_timestamp = self.get_modification_timestamp()
        dt_utc = datetime.fromtimestamp(mod_timestamp, UTC)
        return dt_utc


@dataclass
class HostDirManager(HostDirManagerInterface):
    """Класс менеджера папки на хосте"""

    host_dir: Path

    def iterate_files(self, pattern="*") -> Iterator[Path]:
        """
        Итератор файлов, размещенных в папке host_dir

        :param pattern: маска выбора файлов
        :return: итератор файлов
        """

        return self.host_dir.glob(pattern)

    def get_info(self) -> dict[str, dict[str, datetime]]:
        """
        Получаем информацию о дате изменения файлов
        :return: stats (dict), где ключ словаря - имя файла, значение словаря - {"modified": datetime}
        """
        info = dict()
        for file in self.iterate_files():
            if file.is_file():
                host_file = HostFile(file)
                info[file.name] = dict(modified=host_file.get_modification_datetime())
        return info
