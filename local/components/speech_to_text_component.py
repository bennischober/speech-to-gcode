import dash
import threading
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from components.speech_to_text.recorder import recorder

POSITIVE_PROMPTS = ["realistic digital portrait", "global illumination",
                    "shot at 8k resolution", "highly detailed", "photo realistic", "masterpiece"]
NEGATIVE_PROMPTS = ["bad art", "low detail", "plain background", "grainy", "low quality",
                    "disfigured", "out of frame", "bad proportions", "distortion", "deformations"]


def get_speech_to_text_component():
    @callback(
        Output("diffusion_prompt", "data"),
        State("diffusion_prompt", "data"),
        Input("text-input", "n_submit"),
        State("text-input", "value")
    )
    def handle_text_input(diffusion_prompt_old, n_submit, diffusion_prompt):
        if n_submit is None:
            return dash.no_update
        print('diffusion_prompt_old', diffusion_prompt_old, 'n_submit',
              n_submit, 'diffusion_prompt', diffusion_prompt)
        return diffusion_prompt

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

    return dbc.Card(
        children=[
            dbc.CardHeader('Speech-To-Text'),
            dbc.CardBody([
                dbc.Container(
                    [
                        html.H5(
                            "Sie können entweder einen Text eingeben oder eine Spracheingabe durch das Mikrofon-Symbol starten."),
                        dbc.InputGroup(
                            [
                                dbc.Input(
                                    id="text-input",
                                    placeholder="Geben Sie einen Text ein...",
                                    class_name="rounded-pill",
                                ),
                                dbc.Button(
                                    html.Span(
                                        className="fas fa-microphone",
                                        id="microphone-icon",
                                        style={"fontSize": "1.5rem"},
                                    ),
                                    id="microphone-button",
                                    color="light",
                                    class_name="rounded-circle p-2",
                                    style={"width": "45px",
                                           "height": "45px"},
                                    disabled=False,
                                ),
                            ],
                            class_name="mb-3 d-flex align-items-center",
                        ),
                        html.Div(id="output"),
                        html.Div(id="microphone-status"),
                        dbc.Accordion(
                            [
                                dbc.AccordionItem(
                                    [
                                        html.P(
                                            "Hier können Sie die Standardwerte für die Bildgenerierung ändern. Positive und negative Prompts sind Wörter, die das neuronale Netz dazu bringen, das Bild in eine bestimmte Richtung zu generieren."),
                                        dbc.Row([
                                            dbc.Col([html.H6("Positive Prompts"), dcc.Checklist(POSITIVE_PROMPTS, POSITIVE_PROMPTS), dbc.Input(id="positive-prompts-input", type="text",
                                                    placeholder="Optional: Geben Sie positive Prompts ein"), dbc.FormText("Hinweis: Um mehrere Werte hinzuzufügen, trennen Sie diese mit einem Komma.")]),
                                            dbc.Col([html.H6("Negative Prompts"), dcc.Checklist(NEGATIVE_PROMPTS, NEGATIVE_PROMPTS), dbc.Input(id="negative-prompts-input", type="text",
                                                    placeholder="Optional: Geben Sie negative Prompts ein"), dbc.FormText("Hinweis: Um mehrere Werte hinzuzufügen, trennen Sie diese mit einem Komma.")])
                                        ]),
                                    ],
                                    title="Standardwerte für Bildgenerierung ändern",
                                ),
                            ],
                            start_collapsed=True
                        ),
                        dbc.Row([
                            dbc.Col([dbc.Button(id="generate-image", children="Bilder generieren",
                                                color="primary", className="mt-3")], width=4),
                            dbc.Col([dbc.Button(id="reset-inputs", children="Eingaben zurücksetzen",
                                                color="danger", className="mt-3")], width=4),
                        ], justify="evenly"),
                    ],
                    className="mt-5",
                ),
            ]),
            dcc.Store('diffusion_prompt')
        ],
        className='mb-4',
        style={
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
        }
    )
