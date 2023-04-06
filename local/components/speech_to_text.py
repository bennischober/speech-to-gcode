import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State


def get_speech_to_text_component():
    return dbc.Card(
        children=[
            dbc.CardHeader('Sprache-zu-Text-Komponente'),
            dbc.CardBody([
                dbc.Input(id='speech-input', placeholder='Sprechen Sie jetzt...', className='whatsapp-textfield'),
                html.Button(html.I(className='fa fa-microphone'), id='start-button', className='whatsapp-textfield'),
                html.Button(html.I(className='fa fa-stop'), id='stop-button', className='whatsapp-textfield', disabled=True),
            ]),
            ],
        className='mb-4',
        style={
            'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
        }
    )