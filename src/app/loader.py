from config import settings
from logger import logger_app


def main():
    pass


if __name__ == "__main__":
    logger_app.info(
        "Программа синхронизации файлов начинает работу с директорией: {}",
        settings.host_dir,
    )
    main()
    logger_app.info("Программа остановлена")
