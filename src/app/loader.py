import sys

import config
from logger_module import logger_app, logger
from processing import processing_factory


def main(settings: config.Settings, logger_app: logger):
    """Функция инициализации и запуска бизнес логики"""
    try:
        processing_task = processing_factory(settings, logger_app)
        processing_task.run_loop()
    except TypeError as exc:
        logger_app.error("Ошибка: <{}> {}", exc.__class__.__name__, exc)
    except KeyboardInterrupt:
        logger_app.debug("Приложение остановлено")
        sys.exit(0)
    except Exception as exc:
        logger_app.error("Ошибка: <{}> {}", exc.__class__.__name__, exc)


if __name__ == "__main__":
    settings = config.get_settings()

    logger_app.info(
        "Программа синхронизации файлов начинает работу с директорией: {}",
        settings.host_dir,
    )
    main(settings, logger_app=logger_app)
