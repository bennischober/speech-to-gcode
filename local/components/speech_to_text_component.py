import dash_bootstrap_components as dbc
from dash import html
from dash import html, dcc
import dash_bootstrap_components as dbc


def get_speech_to_text_component():
    return dbc.Card(
        children=[
            dbc.CardHeader('Sprache-zu-Text-Komponente'),
            dbc.CardBody([
                dbc.Container(
                    [
                        html.H1("Real-time Audio Transcription"),
                        dbc.Button("Start", id="start-button",
                                   color="success", className="mr-2"),
                        dbc.Button("Stop", id="stop-button",
                                   color="danger", className="mr-2"),
                        html.Div(id="transcription-output"),
                        dcc.Interval(id="update-interval",
                                     interval=500, n_intervals=0),
                    ],
                    className="mt-5",
                )
            ]),
        ],
        className='mb-4',
        style={
            'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
        }
    )
