import sys
from pathlib import Path

from dotenv import dotenv_values


BASE_DIR = Path(__file__).parent.absolute()
ENV_FILE_PATH = BASE_DIR / ".env"


class Settings:
    """Класс с настройками приложения"""

    def __init__(self, values: dict):
        """Инициализация объекта"""
        self.__values: dict = values
        self.host_dir: Path = self.__get_host_dir()
        self.cloud_dir: str = self.__get_cloud_dir()
        self.auth_token: str = self.__get_auth_token()
        self.sync_period: int = self.__get_sync_period()
        self.log_file_path: Path = self.__get_log_file_path()

    def _get_env_value(self, env_name) -> str:
        """Получаем значение переменной окружения, если оно есть"""
        env_value = self.__values.get(env_name)
        if not env_value:
            raise EnvironmentError(
                f"Значение переменной окружения '{env_name}' не найдено"
            )
        return env_value

    def __get_host_dir(self) -> Path:
        """Получаем путь к синхронизируемой папке на хосте"""
        host_dir_path_env_name = "HOST_DIR_PATH"
        host_dir = Path(self._get_env_value(host_dir_path_env_name))

        if not host_dir.exists():
            raise FileNotFoundError(f"Путь '{host_dir}' не существует")
        if not host_dir.is_dir():
            raise NotADirectoryError(f"Путь '{host_dir}' должен быть директорией")

        return host_dir

    def __get_cloud_dir(self) -> str:
        """Получаем имя папки в облачном хранилище"""
        cloud_dir_env_name = "CLOUD_DIR"
        cloud_dir = self._get_env_value(cloud_dir_env_name)

        return cloud_dir

    def __get_auth_token(self) -> str:
        """Получаем токен аутентификации"""
        auth_token_env_name = "AUTH_TOKEN"
        auth_token = self._get_env_value(auth_token_env_name)
        if " " in auth_token:
            raise ValueError("Неверный токен")
        return auth_token

    def __get_sync_period(self) -> int:
        """Получаем период синхронизации в секундах"""
        sync_period_env_name = "SYNC_PERIOD"
        sync_period = self._get_env_value(sync_period_env_name)

        try:
            sync_period = int(sync_period)
        except ValueError as exc:
            print(f"Значение периода синхронизации нужно указать цифрами")
            raise exc

        return sync_period

    def __get_log_file_path(self) -> Path:
        """Получаем путь к файлу лога"""
        log_file_path_env_name = "LOG_FILE_PATH"
        log_file_path = Path(self._get_env_value(log_file_path_env_name))
        log_file_path.touch(exist_ok=True)

        if not log_file_path.exists():
            raise FileNotFoundError(f"Путь '{log_file_path}' не существует")

        return log_file_path


def get_settings() -> Settings:
    """Получаем экземпляр класса Setting"""
    try:
        if not ENV_FILE_PATH.exists():
            raise FileNotFoundError("Не найден .env файл")

        env_values = dotenv_values(dotenv_path=ENV_FILE_PATH)
        if not env_values:
            raise ValueError(
                "Необходимо указать переменные окружения и их значения в .env файле"
            )

        return Settings(values=env_values)

    except (EnvironmentError, FileNotFoundError, NotADirectoryError, ValueError) as exc:
        print(f"Ошибка: {exc}")
        sys.exit(1)
