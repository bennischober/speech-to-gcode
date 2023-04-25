import dash
import threading
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from components.speech_to_text.recorder import recorder

transcript = ""


def get_speech_to_text_component(skip_recorder: bool = True, debug: bool = True):
    global transcript

    @callback(
        Output("load-model-status", "children"),
        Input("load-model-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def load_model(n_clicks):
        recorder.load_model()
        return ""

    @callback(
        Output("recorder-status", "children"),
        Input("loading-button", "n_clicks"),
    )
    def start_loading(n_clicks):
        if skip_recorder:
            return "Skipped loading model"
        recorder.load_model()
        return "Model loaded"

    @callback(
        Output("transcription-output", "children"),
        Input("update-interval", "n_intervals"),
        prevent_initial_call=True,
    )
    def update_output(_):
        global transcript
        while not recorder.transcription_queue.empty():
            transcript += recorder.transcription_queue.get() + " "
        return transcript

    @callback(
        Output("output", "children"),
        Output("text-input", "value"),
        Input("text-input", "n_submit"),
        State("text-input", "value"),
        prevent_initial_call=True,
    )
    def handle_text_input(n_submit, text):
        if n_submit:
            return f"You submitted: {text}", ""
        return dash.no_update, dash.no_update

    @callback(
        Output("microphone-icon", "className"),
        Output("microphone-button", "color"),
        Output("microphone-button", "disabled"),
        Output("microphone-status", "children"),
        Input("microphone-button", "n_clicks"),
        Input("text-input", "value"),
        State("microphone-button", "color"),
        prevent_initial_call=True,
    )
    def handle_microphone(n_clicks, text, color):
        ctx = dash.callback_context
        if ctx.triggered:
            input_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if input_id == "microphone-button":
                if color == "light":
                    t = threading.Thread(
                        target=recorder.start_recording, name="start_recording")
                    # t.daemon = True
                    t.start()
                    return "fas fa-microphone", "danger", bool(text), "Microphone ON"
                else:
                    recorder.stop_recording()

                    return "fas fa-microphone", "light", bool(text), "Microphone OFF"
            elif input_id == "text-input.value":
                return "fas fa-microphone", "light", bool(text)
        return "fas fa-microphone", "light", bool(text), ""

    def load_model_button(debug: bool):
        if debug:
            return dbc.Container([
                dbc.Button("Start Loading",
                           id="load-model-button", className="mb-3"),
                html.Div(id="load-model-status", style={"display": "none"})
            ])
        else:
            return html.Div(style={"display": "none"})

    return dbc.Card(
        children=[
            dbc.CardHeader('Speech-To-Text Component'),
            dbc.CardBody([
                html.H1("Audio Transcription"),
                load_model_button(debug),
                dbc.Container(
                    [
                        html.H5(
                            "You can either type in text or use your microphone to record audio."),
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
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
        }
    )
