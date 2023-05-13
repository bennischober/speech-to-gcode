import datetime
import dash
import threading
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
from components.speech_to_text.recorder import recorder
from components.speech_to_text.settings_component import settings, settings_button

POSITIVE_PROMPTS = ["realistic digital portrait", "global illumination",
                    "shot at 8k resolution", "highly detailed", "photo realistic", "masterpiece"]
NEGATIVE_PROMPTS = ["bad art", "low detail", "plain background", "grainy", "low quality",
                    "disfigured", "out of frame", "bad proportions", "distortion", "deformations"]


def get_speech_to_text_component():
    return dbc.Card(
        children=[
            dbc.CardHeader('Speech-To-Text'),
            dbc.CardBody([
                settings,
                dbc.Container(
                    [
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
                        html.H5("oder Text eingeben"),
                        dbc.Textarea(
                            id="text-input",
                            placeholder="Geben Sie einen Text ein...",
                        ),
                        html.Div(id="output"),
                        html.Div(id="microphone-status"),
                        dbc.Row([
                            dbc.Col([dbc.Button(id="generate-image", children="Bilder generieren",
                                                color="primary", className="mt-3")]),
                            dbc.Col([dbc.Button(id="reset-inputs", children="Eingaben zurücksetzen",
                                                color="danger", className="mt-3")]),
                            dbc.Col([settings_button]),
                        ]),
                    ],
                    className="mt-5 mb-5",
                    style={"textAlign": "center"}
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
            dcc.Store("prompt-history", storage_type="local")
        ],
        className='mb-4'
    )


@callback(
    Output("positive-prompts-store", "data", allow_duplicate=True),
    Output("negative-prompts-store", "data", allow_duplicate=True),
    Output("text-input", "value", allow_duplicate=True),
    Output("diffusion_prompt", "data", allow_duplicate=True),
    Output("prompt-history", "data"),
    Input("generate-image", "n_clicks"),
    Input("reset-inputs", "n_clicks"),
    Input("settings-prompts-store", "data"),
    Input("input-prompts-store", "data"),
    Input("positive-prompts-store", "data"),
    Input("negative-prompts-store", "data"),
    Input("prompt-history", "data"),
    prevent_initial_call=True
)
def save_or_reset(images_click: int, reset_click: int, settings: dict, input: str, positive: list, negative: list, history: list):
    triggered_id: str = ctx.triggered_id

    if triggered_id != "generate-image" and triggered_id != "reset-inputs":
        return dash.no_update, dash.no_update, dash.no_update, None, dash.no_update

    if triggered_id == "generate-image":
        prompt: list[str] = positive.copy()
        prompt.append(input)
        diffusion_prompt = {'prompt': prompt, 'negative': negative}
        if history is None:
            history = []
        history.append({"prompt": {
            "positive": positive, "negative": negative, "input": input
        }, "timestamp": datetime.datetime.now()})

        if settings['save_settings']:
            return dash.no_update, dash.no_update, None, diffusion_prompt, history
        # generate image
        return dash.no_update, dash.no_update, None, diffusion_prompt, history
    return POSITIVE_PROMPTS, NEGATIVE_PROMPTS, dash.no_update, None, dash.no_update


@callback(
    Output("input-prompts-store", "data", allow_duplicate=True),
    Output('toggle-icon', 'className'),
    Output('toggle-output', 'children'),
    Output("toggle-button", "disabled"),
    Output("text-input", "disabled"),
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

        return text or dash.no_update, new_class, recording_status, bool(text_input), text_disabled

    return text or dash.no_update, current_class, 'Aufnahme starten', bool(text_input), text_disabled
