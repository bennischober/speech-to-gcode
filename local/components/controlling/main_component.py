from dash import html
from dash import dcc

button_style = {
    'background-color': '#333333',
    'color': '#ffffff',
    'font-size': '20px',
    'padding': '10px 20px',
    'border-radius': '50px',
    'margin': '5px 10px',
    "width": "15vw",
}

button_hover_style = {
    'background-color': '#ffffff',
    'color': '#333333'
}

button_click_style = {
    'background-color': '#ff0000',
    'color': '#ffffff'
}


def FuturisticButtons():
    return html.Div([
        html.Div([
            html.Button('Fräsen', id='button-1', style=button_style),
            html.Button('Speichern', id='button-2', style=button_style),
        ], 
       ),
        html.Button('Erneute Aufnahme', id='button-3', style=button_style),
    ], 
    style={
        'display': 'flex',
        'justify-content': 'center',
        'align-items': 'center', 
        'flex-direction': 'column', 
        'height': '200px'
        })



