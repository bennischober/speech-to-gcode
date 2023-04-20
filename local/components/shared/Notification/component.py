"""
This module is used to create a notification component. The component can be used to display a notification to the user. The notification can be closed by the user or will disappear after a certain amount of time.
"""

from uuid import uuid4
import dash_bootstrap_components as dbc
from dash import Input, Output, State
from dash import Dash
from utils.callback_handler import add_callback


def get_notification_component(message: str, id: str = str(uuid4()), duration: int = 4000):
    return dbc.Alert(
        message,
        id=id,
        is_open=True,
        duration=duration,
    )


def get_callback(app: Dash):
    @app.callback(
        Output("alert-auto", "is_open"),
        [Input("alert-toggle-auto", "n_clicks")],
        [State("alert-auto", "is_open")],
    )
    def toggle_alert(n, is_open):
        if n:
            return not is_open
        return is_open


add_callback(get_callback)
