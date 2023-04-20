"""
This module is used to store the state of the application.
"""

from utils.logger import get_logger

log = get_logger(__name__)

state: dict[str, ] = {}


def get_state(key: str):
    return state.get(key, None)


def set_state(key: str, value) -> None:
    state[key] = value


def print_state() -> None:
    log.info(state)
