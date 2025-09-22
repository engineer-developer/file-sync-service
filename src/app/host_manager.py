from os import stat_result

from datetime import datetime, UTC
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from config import settings


@dataclass
class HostFile:
    """Класс файла на хосте"""

    file: Path

    def get_file_statinfo(self) -> stat_result:
        """Получаем информацию о файле"""
        stat = self.file.stat()
        return stat

    def get_modification_timestamp(self) -> int:
        """Получаем timestamp модификации файла"""
        timestamp = int(self.get_file_statinfo().st_mtime)
        return timestamp

    def get_modification_datetime(self) -> datetime:
        """Получаем дату и время модификации файла"""
        mod_timestamp = self.get_modification_timestamp()
        dt_utc = datetime.fromtimestamp(mod_timestamp, UTC)
        return dt_utc


@dataclass
class HostDirManager:
    """Класс менеджера папки на хосте"""

    host_dir: Path

    def get_files_list(self, pattern="*") -> list[Path]:
        """Получаем список файлов в папке"""
        return list(self.host_dir.glob(pattern))

    def iterate_files(self, pattern="*") -> Iterator[Path]:
        """Получаем итератор файлов в папке"""
        return self.host_dir.glob(pattern)

    def get_files_stats(self) -> dict[str, dict[str, datetime]]:
        """
        Получаем информацию о дате и времени изменения файлов
        :return: stats (dict), где:
        ключ словаря - имя файла, значение словаря - {"modified": datetime}
        """
        stats = dict()
        for file in self.iterate_files():
            host_file = HostFile(file)
            stats[file.name] = dict(modified=host_file.get_modification_datetime())
        return stats


host_dir_manager = HostDirManager(settings.host_dir)
host_dir_manager.get_files_stats()
