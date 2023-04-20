import dash_bootstrap_components as dbc
from dash import html
from dash import html, dcc
import dash_bootstrap_components as dbc
from utils.app_state import get_state

def get_speech_to_text_component():
    return dbc.Card(
        children=[
            dbc.CardHeader('Speech-To-Text Component'),
            dbc.CardBody([
                html.H1("Audio Transcription"),
                load_model_button(),
                dbc.Container(
                    [
                        html.H5("You can either type in text or use your microphone to record audio."),
                        dbc.Button("Start Loading",
                                   id="loading-button", className="mb-3", style={"display": "none"}),
                        dbc.InputGroup(
                            [
                                dbc.Input(
                                    id="text-input",
                                    placeholder="Enter text...",
                                    className="rounded-pill",
                                ),
                                dbc.Button(
                                    html.Span(
                                        className="fas fa-microphone",
                                        id="microphone-icon",
                                        style={"fontSize": "1.5rem"},
                                    ),
                                    id="microphone-button",
                                    color="light",
                                    className="rounded-circle p-2",
                                    style={"width": "45px",
                                           "height": "45px"},
                                    disabled=False,
                                ),
                            ],
                            className="mb-3 d-flex align-items-center",
                        ),
                        html.Div(id="recorder-status"),
                        html.Div(id="output"),
                        html.Div(id="microphone-status"),
                        html.Div(id="transcription-output"),
                        dcc.Interval(id="update-interval",
                                     interval=500, n_intervals=0),
                    ],
                    className="mt-5",
                ),
            ]),
        ],
        className='mb-4',
        style={
            'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
        }
    )


def load_model_button():
    if get_state("debug"):
        return dbc.Container([
            dbc.Button("Start Loading",
                       id="load-model-button", className="mb-3"),
            html.Div(id="load-model-status", style={"display": "none"})
        ])
    else:
        return html.Div(style={"display": "none"})
