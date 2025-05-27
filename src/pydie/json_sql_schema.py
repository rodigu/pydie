from enum import Enum
from datetime import datetime


def get_format(date_string: str) -> str:
    """Extracts date formatting from given date string

    :param str date_string: date string in the format `datetime[FORMATTING]`
    :return str:

    >>> get_format('datetime[%Y-%d]')
    '%Y-%d'
    """
    return date_string.strip().split("[")[-1][:-1]
