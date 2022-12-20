import platform
from typing import Any

from knxrcore.logger import Logger


def is_linux() -> bool:
    """ Check for the linux only statements
    :return: Bool
    """
    return 'linux' in platform.platform().lower()


def check_for_new_logins(last_login: bytes, logger: Logger, sub_res: Any) -> tuple:
    """ Check for new logins inside coming over ssh

    :param last_login: The last cached login
    :param logger: The current logger
    :param sub_res: The subprocess response for the 'last' call
    :return: tuple with the new 'last_login' and a status code
    """

    if last_login != sub_res.stdout:
        if last_login == b'':
            last_login = sub_res.stdout
            return last_login, 0

        last_login = sub_res.stdout
        logger.warning(f'New user login: {last_login}')
        return last_login, 0

    return b'Error', 1


def get_limits(config: dict) -> tuple:
    """ Get the predefined limits

    :param config: Give the config as a dict
    :return: Returns the extracted limits
    """

    cpu_limits = (config['hard'].get('cpu', 95), config['hard'].get('cpu', 80))
    ram_limits = (config['hard'].get('ram', 90), config['hard'].get('ram', 80))
    drive_limits = (config['hard'].get('drive', 90), config['hard'].get('drive', 70))
    return cpu_limits, drive_limits, ram_limits


def limit_check(limits: tuple, comp_usage: float, logger: Logger, comp_name: str) -> tuple:
    """ Check the limits from components

    :param limits: The predefined component Limits
    :param comp_usage: The current component usage float
    :param logger: The current logger used
    :param comp_name: The component for the api request
    :return: A tuple with the return code of the api and function

    """

    if comp_usage >= limits[1]:
        if comp_usage >= limits[0]:
            res = logger.error(f'{comp_name.title()} has exceeded its hard limits') \
                .get_api(f'burn/1337/{comp_name.lower()}/{comp_usage}/1')

            return 0, res.status_code if not isinstance(res, int) else res

        res = logger.warning(f'{comp_name.title()} has exceeded its soft limits') \
            .get_api(f'burn/1337/{comp_name.lower()}/{comp_usage}/0')

        return 0, res.status_code if not isinstance(res, int) else res

    return 1, 404
