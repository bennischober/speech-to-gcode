import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, State
import dash_bootstrap_components as dbc

def _create_tabs(prefix: str):
    return dbc.Tab([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H6(
                        f"{prefix.capitalize()} Prompts"),
                    dbc.Checklist(
                        id=f"{prefix}-prompts-checklist")
                ]),
                dbc.Col([
                    dbc.InputGroup([
                        dbc.Input(id=f"{prefix}-prompts-input", type="text",
                                  placeholder=f"Optional: Geben Sie einen {prefix}n Prompt ein"),
                        dbc.Button(
                            id=f"add-{prefix}-prompt", children="Hinzufügen", n_clicks=0)
                    ])
                ]),
            ]),
        ],
            className="m-3"
        ),
    ], label=f"{prefix.capitalize()} Prompts", tab_id=prefix)

def _create_callbacks(prefix: str):
    @callback(
    Output(f"{prefix}-prompts-checklist", "options"), # update its options => add new prompt
    Output(f"{prefix}-prompts-checklist", "value"), # update selected => only needed on initial call
    Output(f"{prefix}-prompts-store", "data"), # update store => add new prompt
    Output(f"{prefix}-prompts-input", "value"), # clear input
    Input(f"add-{prefix}-prompt", "n_clicks"), # add prompt on click
    Input(f"{prefix}-prompts-store", "data"), # get prompts from store
    Input(f"{prefix}-prompts-checklist", "value"), # get selected prompts
    State(f"{prefix}-prompts-input", "value") # get prompt from input
    )
    def update_prompts(n_clicks, prompts, selected, value):
        if value is None or value == "":
            return prompts, prompts, prompts, None
        # this is only the initial call
        if selected is None or selected == "":
            return prompts, prompts, prompts, None
        # just selection is changed
        if n_clicks is None or n_clicks == 0:
            return prompts, selected, prompts, None
        # new input
        if n_clicks > 0 and value not in prompts:
            prompts.append(value)
        return prompts, selected, prompts, None


_create_callbacks("positive")
_create_callbacks("negative")

@callback(
    Output("modal", "is_open"),
    Input("open", "n_clicks"),
    Input("close", "n_clicks"),
    State("modal", "is_open"),
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# EXPORTS

settings_button = dbc.Button(id="open", children="Einstellungen",
                             color="secondary", className="mt-3")

settings = dbc.Modal(
    [
        dbc.ModalHeader(
            dbc.ModalTitle("Einstellungen")),
        dbc.ModalBody([
            html.P(
                "Hier können Sie die Standardwerte für die Bildgenerierung ändern. Positive und negative Prompts sind Wörter, die das neuronale Netz dazu bringen, das Bild in eine bestimmte Richtung zu generieren."),
            dbc.Tabs(
                [
                    _create_tabs("positive"),
                    _create_tabs("negative"),

                ]
            ),
        ]),
        dbc.ModalFooter(
            dbc.Button(
                "Speichern", id="close", className="ms-auto", n_clicks=0
            )
        ),
    ],
    id="modal",
    is_open=False,
    size="xl",
)
