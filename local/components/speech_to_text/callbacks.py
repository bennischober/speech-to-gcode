import dash
from dash import Dash
from dash.dependencies import Input, Output, State
import threading
from components.speech_to_text.recorder import recorder
from utils.app_state import get_state
from utils.callback_handler import add_callback

transcript = ""

def get_callbacks(app: Dash):
    """
    Creates all callback functions for the speech to text component. Needs a reference to the ``Dash`` application to create the callbacks. ``skip_recorder`` can be set to ``True`` to skip the transcription. Useful in front-end development, because model loading takes a while.
    """

    skip_recorder = get_state("skip_recorder")

    @app.callback(
        Output("load-model-status", "children"),
        Input("load-model-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def load_model(n_clicks):
        recorder.load_model()
        return ""

    @app.callback(
        Output("recorder-status", "children"),
        Input("loading-button", "n_clicks"),
    )
    def start_loading(n_clicks):
        if skip_recorder:
            return "Skipped loading model"
        recorder.load_model()
        return "Model loaded"

    @app.callback(
        Output("transcription-output", "children"),
        Input("update-interval", "n_intervals"),
        prevent_initial_call=True,
    )
    def update_output(_):
        global transcript
        while not recorder.transcription_queue.empty():
            transcript += recorder.transcription_queue.get() + " "
        return transcript

    @app.callback(
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

    @app.callback(
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

# register the callbacks for the speech_to_text component
add_callback(get_callbacks)
