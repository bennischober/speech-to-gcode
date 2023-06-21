import requests
import threading
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
from components.speech_to_text.recorder import recorder
from components.speech_to_text.settings_component import settings, settings_button
from utils.config import POSITIVE_PROMPTS, NEGATIVE_PROMPTS, TEXT_ENDPOINT


def get_speech_to_text_component():
    return dbc.Card(
        children=[
            dbc.CardHeader('Speech-To-Text'),
            dbc.CardBody([
                settings,
                html.Div(id='recording-status', style={'display': 'none'}),
                html.Div(id='response-status', style={'display': 'none'}),
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
                                                'negative': '', 'search_prompt': 'house . pool . '}),
            dcc.Store(id='input-prompts-store', storage_type='session',
                      data={'prompt': "Ein Haus mit einem Pool", 'type': 'text'}),
            dcc.Store(id="search-prompt-store", storage_type="session", data="house . pool . "),
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
    State("search-prompt-store", "data"),
    prevent_initial_call=True
)
def save_or_reset(images_click: int, reset_click: int, input: dict, positive: list, negative: list, search_prompt: str):
    triggered_id: str = ctx.triggered_id

    if triggered_id == "generate-image":
        if input['type'] == 'text':
            # make request to text pipeline
            response = requests.post(TEXT_ENDPOINT, json={'text': input['prompt']})
            data = response.json()

            translated_p = data['prompt']
            search_p = data['search_prompt']
            
            diffusion_prompt = create_diffusion_prompt(
                translated_p, positive, negative, search_p)
            
            return diffusion_prompt

        diffusion_prompt = create_diffusion_prompt(
            input['prompt'], positive, negative, search_prompt)
        
        return diffusion_prompt

    # elif triggered_id == "reset-inputs":
    #     return None
    else:
        return dash.no_update

def create_diffusion_prompt(prompt: str, positive, negative, search_prompt: str):
    prompt: list[str] = [prompt]
    prompt.extend(positive)

    # map prompt and negative to whitespace separated string
    prompt = ", ".join(prompt)
    negative = ", ".join(negative)

    return {'prompt': prompt, 'negative': negative, 'search_prompt': search_prompt}

@callback(
    Output("input-prompts-store", "data"),
    Output('toggle-icon', 'className'),
    Output('toggle-output', 'children'),
    Output("toggle-button", "disabled"),
    Output("text-input", "disabled"),
    Output("recording-status", "children"),
    Output('notification-toast', 'header'),
    Output('notification-toast', 'children'),
    Output('notification-toast', 'icon'),
    Output('notification-toast', 'is_open'),
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

    notification_header = ""
    notification_body = []
    notification_icon = ""
    notification_open = False

    text_dict = {'prompt': text_input, 'type': 'text'} if text_input else None

    if ctx.triggered_id == 'toggle-button':
        if 'fas fa-microphone-slash' in current_class:
            new_class = 'fas fa-microphone'
            recording_status = 'Aufnahme stoppen'
            is_recording = 'true'
        else:
            mic_disabled = True
            is_recording = 'false'
            text_disabled = True

            notification_header = "Spracheingabe wird verarbeitet"
            notification_body = [html.P("Bitte warten Sie, während die Spracheingabe verarbeitet wird...", className="mb-0")]
            notification_icon = "info"
            notification_open = True

    return text_dict or dash.no_update, new_class, recording_status, mic_disabled, text_disabled, is_recording or dash.no_update, notification_header, notification_body, notification_icon, notification_open


@callback(
    Output("input-prompts-store", "data", allow_duplicate=True),
    Output("search-prompt-store", "data", allow_duplicate=True),
    Output("current-prompt", "children", allow_duplicate=True),
    Output("toggle-button", "disabled", allow_duplicate=True),
    Output("text-input", "disabled", allow_duplicate=True),
    Output('notification-toast', 'is_open', allow_duplicate=True),
    Output('response-status', 'children', allow_duplicate=True),
    Input("recording-status", "children"),
    State("text-input", "value"),
    prevent_initial_call=True
)
def toggle_recording(is_recording: str, text_input: str):
    text = {'prompt': text_input, 'type': 'text'} if text_input else None
    text_disabled = True
    search = None
    translated_text = None
    status = None

    if is_recording == 'true':
        t = threading.Thread(
            target=recorder.start_recording, name="start_recording")
        t.start()
    elif is_recording == 'false':
        text_response, search = recorder.stop_recording()
        text = {'prompt': text_response, 'type': 'audio'}
        translated_text = text_response
        text_disabled = False
        status = 'ok'

    return text or dash.no_update, search or dash.no_update, translated_text or dash.no_update, False, text_disabled, False, status or dash.no_update

@callback(
    Output('notification-toast', 'header', allow_duplicate=True),
    Output('notification-toast', 'children', allow_duplicate=True),
    Output('notification-toast', 'icon', allow_duplicate=True),
    Output('notification-toast', 'is_open', allow_duplicate=True),
    Output('notification-toast', 'duration', allow_duplicate=True),
    Input("response-status", "children"),
    prevent_initial_call=True
)
def update_response_notification(status: str):
    if status == "ok":
        return "Verarbeitung erfolgreich",  [html.P("Die Spracheingabe wurde erfolgreich verarbeitet. Bilder können generiert werden!", className="mb-0")], "success", True, 5000
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
