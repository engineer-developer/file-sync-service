from dataclasses import dataclass

from cloud_manager import CloudDirManager
from host_manager import HostDirManager
from logger import logger_app


@dataclass
class Comparator:
    host_dir_manager: HostDirManager
    cloud_dir_manager: CloudDirManager

    def compare_files(self):
        """Метод сравнения файлов на хосте и в облачном хранилище"""

        host_files_stats = self.host_dir_manager.get_files_stats()
        cloud_files_stats = self.cloud_dir_manager.get_files_stats()

        # Проходим по всем файлам из облачного хранилища.
        for cloud_file_name in cloud_files_stats:
            # Проверяем есть ли облачный файл в папке на хосте.
            if cloud_file_name not in host_files_stats:
                # Если нет, удаляем файл из облачного хранилища.
                file_path = self.host_dir_manager.host_dir / cloud_file_name
                self.cloud_dir_manager.delete_file(file_path)

        # Если есть, но время его изменения позже, чем в облаке, загружаем его в облачное хранилище повторно
        # - то есть обновляем.
        # Проходим по всем файлам из папки на хосте.
        for host_file_name in host_files_stats:
            # Проверяем есть ли локальный файл в облачном хранилище.
            if host_file_name not in cloud_files_stats:
                # Если нет, загружаем файл в облачное хранилище.
                host_file_path = self.host_dir_manager.host_dir / host_file_name
                self.cloud_dir_manager.upload_file(host_file_path)

            else:
                # Если есть, выполняем метод сравнения даты и времени модификации файлов
                host_file_stat = host_files_stats.get(host_file_name)
                logger_app.debug("host_file_stat: {}", host_file_stat)
                cloud_file_stat = cloud_files_stats.get(host_file_name)
                logger_app.debug("cloud_file_stat: {}", cloud_file_stat)

    def compare_files_modification_date(
        self, host_filename: str, host_file_st: dict, cloud_file_st: dict
    ):
        """Сравниваем дату и время модификации файлов"""
        host_file_mod_dt = host_file_st.get("modified")
        logger_app.debug("host_file modification datetime: {}", host_file_mod_dt)
        cloud_file_mod_dt = cloud_file_st.get("modified")
        logger_app.debug("cloud_file modification datetime: {}", cloud_file_mod_dt)
        if host_file_mod_dt > cloud_file_mod_dt:
            host_file_path = self.host_dir_manager.host_dir / host_filename
            self.cloud_dir_manager.update_file(host_file_path)
