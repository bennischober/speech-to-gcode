from dash import html
import dash_bootstrap_components as dbc


gcode_state_success_layout = [
    html.Div("GCode erfolgreich erstellt!", style={'font-size': '15px'}),
    html.Div(
        html.I(
            className='bi bi-check-lg gcode_status_icon gcode_status_success',
                style={
                    'font-size': '30px',
                }),
            id='icon'),
]

gcode_state_error_layout = [
    html.Div("GCode konnte nicht erstellt werden!", style={'font-size': '15px'}),
    html.Div(
        html.I(
            className='bi bi-x-lg gcode_status_icon gcode_status_error',
                style={
                    'font-size': '30px',
                }),
            id='icon'),
]

gcode_content_layout = [
    dbc.Button("Hier Klicken, um den Code anzuzeigen", id="show_gcode_button", className="mt-3 show_gcode_button"),
    dbc.Collapse([
        html.H6("G-Code:"),
        dbc.CardBody([
            html.Pre(
                id='gcode_visualization', children=[], className='gcode_style')
        ]),
    ], style={'background': '#ffffff', 'margin': 'auto', 'width': '60vw'}, id="show_gcode", is_open=False),
    html.Div("Bereit zum Fräßen!"),
    html.Div("Klicken Sie auf     -Erneute Aufnahme-     um ein weiteres Bild zu generieren!"),
]