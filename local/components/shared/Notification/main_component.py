import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc


def notifications():
    return dbc.Toast(
        id="notification-toast",
        header="Notification",
        icon="info",
        dismissable=True,
        is_open=False,
        style={"position": "fixed", "top": 66, "right": 10, "width": 350},
    )

@callback(
    Output('notification-toast', 'header', allow_duplicate=True),
    Output('notification-toast', 'children', allow_duplicate=True),
    Output('notification-toast', 'icon', allow_duplicate=True),
    Output('notification-toast', 'is_open', allow_duplicate=True),
    Output('notification-toast', 'duration', allow_duplicate=True),
    Input('generate-image', 'n_clicks'),
    Input('generate_diff_imges', 'n_clicks'),
    Input('reset-inputs', 'n_clicks'),
    prevent_initial_call=True,
)
def notify(n1, n2, n3):
    print("calling notify", ctx.triggered)
    if ctx.triggered_id == 'generate-image':
        print("generating images")
        return "Bilder generieren" ,[html.P("Bilder werden generiert, bitte warten...", className="mb-0")], "info", True, None
    elif ctx.triggered_id == 'generate_diff_imges':
        return "Bilder neu generieren" ,[html.P("Bilder werden neu generiert, bitte warten...", className="mb-0")], "info", True, None
    elif ctx.triggered_id == 'reset-inputs':
        return "Erfolgreich", [html.P("Eingaben wurden zurückgesetzt.", className="mb-0")], "success", True, 5000
