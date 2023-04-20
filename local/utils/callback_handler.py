"""
This module is used to register callbacks in the Dash app. Callbacks are registered by adding them to the ``callbacks`` list. The ``register_callback`` function then registers all callbacks in the list on app start.
"""

from typing import Callable
import utils.logger as logger
from dash import Dash

log = logger.get_logger(__name__)

callbacks: list[Callable[[], None]] = []


def add_callback(callback: Callable[[], None]):
    """
    Adds a callback to the list of callbacks to be registered
    """
    callbacks.append(callback)


def register_callback(app: Dash):
    """
    Registers all callbacks in the Dash app on start
    """
    log.info("Registering all callbacks")
    for callback in callbacks:
        callback(app)
