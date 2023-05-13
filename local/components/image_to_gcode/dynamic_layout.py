from dash import html
import dash_bootstrap_components as dbc

code_style = {
    "color": "black",
    "white-space": "pre-wrap",
    "word-wrap": "break-word",
    'text-align': 'left',
    'color': '#000000',
    'margin-left': '10px'
}

gcode_state_success_layout = [
    html.Div("GCode erfolgreich erstellt!", style={'font-size': '15px'}),
    html.Div(
        html.I(
            className='bi bi-check-lg',
                style={
                    'font-size': '30px',
                }),
            id='icon',
            style={
                "border-radius": "50%",
                "background-color": "green",
                "width": "50px",
                "height": "50px",
                'margin': 'auto',
                'display': 'flex',
                'justify-content': 'center',
                'align-items': 'center'
    }),
]

gcode_state_error_layout = [
    html.Div("GCode konnte nicht erstellt werden!", style={'font-size': '15px'}),
    html.Div(
        html.I(
            className='bi bi-x-lg',
                style={
                    'font-size': '30px',
                }),
            id='icon',
            style={
                "border-radius": "50%",
                "background-color": "red",
                "width": "50px",
                "height": "50px",
                'margin': 'auto',
                'display': 'flex',
                'justify-content': 'center',
                'align-items': 'center'
    }),
]

gcode_content_layout = [
    dbc.Button("Hier Klicken, um den Code anzuzeigen", id="show_gcode_button", className="mt-3", style={
               'width': '60vw', 'margin': 'auto', 'margin-bottom': '20px', 'color': '#ffffff'}),
    dbc.Collapse([
        html.H6("G-Code:"),
        dbc.CardBody([
            html.Pre(
                id='gcode_visualization', children=[], style=code_style)
        ]),
    ], style={'background': '#ffffff', 'margin': 'auto', 'width': '60vw'}, id="show_gcode", is_open=False),
    html.Div("Bereit zum Fräßen!"),
    html.Div("Klicken Sie auf     -Erneute Aufnahme-     um ein weiteres Bild zu generieren!"),
]