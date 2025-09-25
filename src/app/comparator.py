from dataclasses import dataclass

from cloud_manager import CloudDirManagerInterface
from host_manager import HostDirManagerInterface


@dataclass
class Comparator:
    """Класс осуществляющий сравнение файлов на хосте и в облачном хранилище"""

    host_dir_manager: HostDirManagerInterface
    cloud_dir_manager: CloudDirManagerInterface

    def compare_files(self):
        """Метод сравнения файлов на хосте и в облачном хранилище"""

        host_files_info = self.host_dir_manager.get_info()
        cloud_files_info = self.cloud_dir_manager.get_info()

        # Проходим по всем файлам из облачного хранилища.
        for cloud_file_name in cloud_files_info:
            # Проверяем есть ли облачный файл в папке на хосте.
            if cloud_file_name not in host_files_info:
                # Если нет, удаляем файл из облачного хранилища.
                file_path = self.host_dir_manager.host_dir / cloud_file_name
                self.cloud_dir_manager.delete(file_path)

        # Проходим по всем файлам из папки на хосте.
        for host_file_name in host_files_info:
            # Проверяем есть ли локальный файл в облачном хранилище.
            if host_file_name not in cloud_files_info:
                # Если нет, загружаем файл в облачное хранилище.
                host_file_path = self.host_dir_manager.host_dir / host_file_name
                self.cloud_dir_manager.load(host_file_path)

            else:
                # Если есть, выполняем метод сравнения даты и времени модификации файлов
                host_file_stat = host_files_info.get(host_file_name)
                cloud_file_stat = cloud_files_info.get(host_file_name)
                self.compare_files_modification_date(
                    host_filename=host_file_name,
                    host_file_st=host_file_stat,
                    cloud_file_st=cloud_file_stat,
                )

    def compare_files_modification_date(
        self, host_filename: str, host_file_st: dict, cloud_file_st: dict
    ) -> None:
        """Сравниваем дату и время модификации файлов"""
        host_file_mod_dt = host_file_st.get("modified")
        cloud_file_mod_dt = cloud_file_st.get("modified")

        # Если дата файла на хосте позже даты в облачном хранилище,
        # то обновляем облачный файл более новой версией с хоста
        if host_file_mod_dt > cloud_file_mod_dt:
            host_file_path = self.host_dir_manager.host_dir / host_filename
            self.cloud_dir_manager.reload(host_file_path)
