import time
from dataclasses import dataclass

import config
import logger_module
from comparator import Comparator
from host_manager import HostDirManager
from cloud_manager import CloudDirManager


@dataclass
class Processing:
    """Класс выполнения сравнения в цикле"""

    sync_period: int
    comparator: Comparator
    logger_app: logger_module.logger

    def run_loop(self) -> None:
        """
        Запускаем цикл обработки задачи сравнения,
        который выполняется бесконечно с заданным периодом
        """
        while True:
            try:
                self.comparator.compare_files()
                time.sleep(self.sync_period)
            except Exception as exc:
                self.logger_app.error("Ошибка: <{}> {}", exc.__class__.__name__, exc)


def processing_factory(
    settings: config.Settings, logger_app: logger_module.logger
) -> Processing:
    """
    Функция инициализации задача обработки
    :param settings: объект настроек приложения
    :param logger_app: объект для логирования
    :return: processing_task - объект обработчика
    """
    host_manager = HostDirManager(
        host_dir=settings.host_dir,
    )
    cloud_manager = CloudDirManager(
        token=settings.auth_token,
        cloud_dir=settings.cloud_dir,
        logger_app=logger_app,
    )

    comparator = Comparator(
        host_dir_manager=host_manager,
        cloud_dir_manager=cloud_manager,
    )

    processing_task = Processing(
        sync_period=settings.sync_period,
        comparator=comparator,
        logger_app=logger_app,
    )
    return processing_task
