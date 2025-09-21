import os

from dotenv import dotenv_values


env_values = dotenv_values(".env")
if not env_values:
    raise ValueError("Must specify envs in .env file")


class Settings:
    """Класс с настройками приложения"""

    def __init__(self, values: dict):
        self.values: dict = values
        self.host_dir: str = self._get_host_dir()
        self.cloud_dir: str = self._get_cloud_dir()
        self.auth_token: str = self._get_auth_token()
        self.sync_period: int = self._get_sync_period()
        self.log_file_path: str = self._get_log_file_path()

    def _get_env_value(self, env_name) -> str:
        """Получаем значение переменной окружения, если оно есть"""
        env_value = self.values.get(env_name)
        if not env_value:
            raise EnvironmentError(
                f"Значение переменной окружения '{env_name}' не найдено"
            )
        return env_value

    def _get_host_dir(self) -> str:
        """Получаем путь к синхронизируемой папке на хосте"""
        host_dir_path_env_name = "HOST_DIR_PATH"
        host_dir = self._get_env_value(host_dir_path_env_name)

        is_exists = os.path.exists(host_dir)
        if not is_exists:
            raise FileNotFoundError(f"Путь '{host_dir}' не существует")

        return host_dir

    def _get_cloud_dir(self) -> str:
        """Получаем имя папки в облачном хранилище"""
        cloud_dir_env_name = "CLOUD_DIR"
        cloud_dir = self._get_env_value(cloud_dir_env_name)

        return cloud_dir

    def _get_auth_token(self) -> str:
        """Получаем токен аутентификации"""
        auth_token_env_name = "AUTH_TOKEN"
        auth_token = self._get_env_value(auth_token_env_name)
        if " " in auth_token:
            raise ValueError("Неверный токен")
        return auth_token

    def _get_sync_period(self) -> int:
        """Получаем период синхронизации в секундах"""
        sync_period_env_name = "SYNC_PERIOD"
        sync_period = self._get_env_value(sync_period_env_name)

        try:
            sync_period = int(sync_period)
        except ValueError as exc:
            print(f"Ошибка: значение периода синхронизации нужно указать цифрами")
            raise exc

        return sync_period

    def _get_log_file_path(self) -> str:
        """Получаем путь к файлу лога"""
        log_file_path_env_name = "LOG_FILE_PATH"
        log_file_path = self._get_env_value(log_file_path_env_name)

        is_exists: bool = os.path.exists(log_file_path)
        if not is_exists:
            raise FileNotFoundError(f"Путь '{log_file_path}' не существует")

        return log_file_path


settings = Settings(values=env_values)
