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
                html.Div(id='recording-status', style={'display': 'none'}),
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
                                                       className='fas fa-microphone-slash',
                                                       style={"fontSize": "3rem"})
                                            ],
                                            disabled=True,
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
                                        dbc.Container(children=[
                                            html.H3("Texteingabe"),
                                            dbc.Textarea(
                                                id="text-input",
                                                placeholder="Geben Sie einen Text ein...",
                                                value="Ein Haus mit einem Pool",
                                                style={"width": "75%", "margin-left": "auto", "margin-right": "auto"}
                                            ),
                                            html.Div(id="output"),
                                        ],
                                            fluid="sm")
                                    ],
                                    className="text-center mt-5",
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
                        ],
                        className="text-center"),
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
            dcc.Store('diffusion_prompt', data={'prompt': 'Ein Haus mit einem Pool',
                                                'negative': ''}),
            dcc.Store(id='input-prompts-store', storage_type='session',
                      data="Ein Haus mit einem Pool"),
            dcc.Store(id="positive-all-prompts-store",
                      storage_type="session", data=POSITIVE_PROMPTS),
            dcc.Store(id="negative-all-prompts-store",
                      storage_type="session", data=NEGATIVE_PROMPTS),
            dcc.Store(id="positive-selected-prompts-store",
                      storage_type="session", data=POSITIVE_PROMPTS),
            dcc.Store(id="negative-selected-prompts-store",
                      storage_type="session", data=NEGATIVE_PROMPTS),
            dcc.Store(id="settings-prompts-store", storage_type="local",
                      data={'save_settings': False}),
        ],
        className='mb-4'
    )


@callback(
    Output("current-prompt", "children"),
    Input("text-input", "value"),
    State('toggle-icon', 'className'),
    # prevent_initial_call=True
)
def update_current_prompt(text_input, current_class):
    if 'fas fa-microphone' in current_class:
        return text_input
    else:
        return recorder.get_latest_recording()


@callback(
    # Output("text-input", "value"),
    Output("diffusion_prompt", "data"),
    Input("generate-image", "n_clicks"),
    Input("reset-inputs", "n_clicks"),
    State("input-prompts-store", "data"),
    State("positive-selected-prompts-store", "data"),
    State("negative-selected-prompts-store", "data"),
    prevent_initial_call=True
)
def save_or_reset(images_click: int, reset_click: int, input: str, positive: list, negative: list):
    triggered_id: str = ctx.triggered_id

    if triggered_id == "generate-image":
        prompt: list[str] = [input]
        prompt.extend(positive)

        # map prompt and negative to whitespace separated string
        prompt = " ".join(prompt)
        negative = " ".join(negative)

        diffusion_prompt = {'prompt': prompt, 'negative': negative}
        return diffusion_prompt
    # elif triggered_id == "reset-inputs":
    #     return None
    else:
        return dash.no_update

@callback(
    Output("input-prompts-store", "data"),
    Output('toggle-icon', 'className'),
    Output('toggle-output', 'children'),
    Output("toggle-button", "disabled"),
    Output("text-input", "disabled"),
    Output("recording-status", "children"),
    Input('toggle-button', 'n_clicks'),
    Input("text-input", "value"),
    State('toggle-icon', 'className')
)
def toggle_icon(mic_click: int, text_input: str, current_class: str):
    new_class = 'fas fa-microphone-slash'
    recording_status = 'Aufnahme starten'
    mic_disabled = bool(text_input)
    is_recording = None
    text_disabled = False

    if ctx.triggered_id == 'toggle-button':
        if 'fas fa-microphone-slash' in current_class:
            new_class = 'fas fa-microphone'
            recording_status = 'Aufnahme stoppen'
            is_recording = 'true'
        else:
            mic_disabled = True
            is_recording = 'false'
            text_disabled = True

    return text_input or dash.no_update, new_class, recording_status, mic_disabled, text_disabled, is_recording or dash.no_update

@callback(
    Output("input-prompts-store", "data", allow_duplicate=True),
    Output("current-prompt", "children", allow_duplicate=True),
    Output("toggle-button", "disabled", allow_duplicate=True),
    Output("text-input", "disabled", allow_duplicate=True),
    Input("recording-status", "children"),
    State("text-input", "value"),
    prevent_initial_call=True
)
def toggle_recording(is_recording: str, text_input: str):
    text = text_input
    text_disabled = True

    if is_recording == 'true':
        t = threading.Thread(
            target=recorder.start_recording, name="start_recording")
        t.start()
    elif is_recording == 'false':
        text = recorder.stop_recording()
        text_disabled = False

    return text or dash.no_update, text or dash.no_update, False, text_disabled

