import dash
import threading
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
from components.speech_to_text.recorder import recorder
from components.speech_to_text.settings_component import settings, settings_button
from utils.config import POSITIVE_PROMPTS, NEGATIVE_PROMPTS


def get_speech_to_text_component():
    return dbc.Card(
        children=[
            dbc.CardHeader('Speech-To-Text'),
            dbc.CardBody([
                settings,
                dbc.Container(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H3("Spracheingabe"),
                                        dbc.Button(
                                            id='toggle-button',
                                            style={
                                                "backgroundColor": "transparent",
                                                "border": "none",
                                                "outline": "none",
                                                "cursor": "pointer"
                                            },
                                            children=[
                                                html.I(id='toggle-icon',
                                                       className='fas fa-microphone',
                                                       style={"fontSize": "3rem"})
                                            ]
                                        ),
                                        html.Div(id='toggle-output',
                                                 children='Aufnahme starten'),
                                        html.Div(id="microphone-status"),
                                    ],
                                    className="text-center mt-5",
                                ),
                                dbc.Col(
                                    style={"border-left": "2px solid #ccc"},
                                    children=[
                                        html.H3("Texteingabe"),
                                        dbc.Textarea(
                                            id="text-input",
                                            placeholder="Geben Sie einen Text ein...",
                                        ),
                                        html.Div(id="output"),
                                    ],
                                    className="mt-5",
                                ),
                            ],
                            className="mb-5",
                        ),
                        html.Hr(),
                        html.Div(children=[
                            html.Span(children=[
                                html.H5("Aktuelle Eingabe: "),
                            ], style={'display': 'inline-block', 'margin-right': '10px'}),
                            html.Span(children=[
                                html.H5(id="current-prompt")
                            ], style={'display': 'inline-block'}),
                        ]),
                        html.Hr(),
                        dbc.Row(
                            [
                                dbc.Col([dbc.Button(id="generate-image", children="Bilder generieren",
                                                    color="primary", className="mt-3")], className="text-center"),
                                dbc.Col([dbc.Button(id="reset-inputs", children="Eingaben zurücksetzen",
                                                    color="danger", className="mt-3")], className="text-center"),
                                dbc.Col([settings_button],
                                        className="text-center"),
                            ],
                            className="mb-5",
                        ),
                    ],
                ),
            ]),
            dcc.Store('diffusion_prompt'),
            dcc.Store(id='input-prompts-store', storage_type='session'),
            dcc.Store(id="positive-prompts-store", storage_type="session",
                      data=POSITIVE_PROMPTS),
            dcc.Store(id="negative-prompts-store", storage_type="session",
                      data=NEGATIVE_PROMPTS),
            dcc.Store("settings-prompts-store", storage_type="local",
                      data={'save_settings': False}),
        ],
        className='mb-4'
    )


@callback(
    Output("current-prompt", "children"),
    Input("text-input", "value"),
    State('toggle-icon', 'className'),
    prevent_initial_call=True
)
def update_current_prompt(text_input, current_class):
    if 'fas fa-microphone' in current_class:
        return text_input
    else:
        return recorder.get_latest_recording()


@callback(
    Output("positive-prompts-store", "data", allow_duplicate=True),
    Output("negative-prompts-store", "data", allow_duplicate=True),
    Output("text-input", "value"),
    Output("diffusion_prompt", "data"),
    Input("generate-image", "n_clicks"),
    Input("reset-inputs", "n_clicks"),
    State("settings-prompts-store", "data"),
    State("input-prompts-store", "data"),
    State("positive-prompts-store", "data"),
    State("negative-prompts-store", "data"),
    prevent_initial_call=True
)
def save_or_reset(images_click: int, reset_click: int, settings: dict, input: str, positive: list, negative: list):
    triggered_id: str = ctx.triggered_id

    if triggered_id == "generate-image":
        prompt: list[str] = positive.copy()
        prompt.append(input)
        # map prompt and negative to whitespace seperated string
        prompt = " ".join(prompt)
        negative = " ".join(negative)

        diffusion_prompt = {'prompt': prompt, 'negative': negative}

        if settings['save_settings']:
            return dash.no_update, dash.no_update, '', diffusion_prompt
        # generate image
        return POSITIVE_PROMPTS, NEGATIVE_PROMPTS, '', diffusion_prompt
    return POSITIVE_PROMPTS, NEGATIVE_PROMPTS, '', None, dash.no_update


@callback(
    Output("input-prompts-store", "data", allow_duplicate=True),
    Output('toggle-icon', 'className'),
    Output('toggle-output', 'children'),
    Output("toggle-button", "disabled"),
    Output("text-input", "disabled"),
    Output("current-prompt", "children", allow_duplicate=True),
    Input('toggle-button', 'n_clicks'),
    Input("text-input", "value"),
    State('toggle-icon', 'className'),
    prevent_initial_call=True
)
def toggle_icon(mic_click: int, text_input: str, current_class: str):
    new_class = 'fas fa-microphone'
    recording_status = 'Aufnahme starten'
    text_disabled = False
    text = text_input

    if ctx.triggered_id == 'toggle-button':
        if 'fas fa-microphone-slash' not in current_class:
            text_disabled = True
            new_class = 'fas fa-microphone-slash'
            recording_status = 'Aufnahme stoppen'
            t = threading.Thread(
                target=recorder.start_recording, name="start_recording")
            t.start()
        else:
            text_disabled = False
            text = recorder.stop_recording()

        return text or dash.no_update, new_class, recording_status, bool(text_input), text_disabled, text or dash.no_update

    return text or dash.no_update, current_class, 'Aufnahme starten', bool(text_input), text_disabled, text or dash.no_update
