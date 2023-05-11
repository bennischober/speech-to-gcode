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
        # update its options => add new prompt
        Output(f"{prefix}-prompts-checklist", "options"),
        # update selected => only needed on initial call
        Output(f"{prefix}-prompts-checklist", "value"),
        # update store => add new prompt
        Output(f"{prefix}-prompts-store", "data"),
        Output(f"{prefix}-prompts-input", "value"),  # clear input
        Input(f"add-{prefix}-prompt", "n_clicks"),  # add prompt on click
        Input(f"{prefix}-prompts-store", "data"),  # get prompts from store
        Input(f"{prefix}-prompts-checklist", "value"),  # get selected prompts
        State(f"{prefix}-prompts-input", "value")  # get prompt from input
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
    Output("settings-modal", "is_open"),
    Output("settings-prompts-store", "data", allow_duplicate=True),
    Output("save-settings-checkbox", "value"),
    Input("settings-modal-open", "n_clicks"),
    Input("settings-modal-save", "n_clicks"),
    Input("settings-prompts-store", "data"),
    State("settings-modal", "is_open"),
    State("save-settings-checkbox", "value"),
    prevent_initial_call=True
)
def toggle_modal(n1: int, n2: int, store: dict, is_open: bool, checked: bool):
    init = store['save_settings'] if checked is None else checked
    store['save_settings'] = init
    if n1 or n2:
        return not is_open, store, init
    return is_open, store, init


# EXPORTS

settings_button = dbc.Button(id="settings-modal-open", children="Einstellungen",
                             color="secondary", className="mt-3")

settings = dbc.Modal(
    [
        dbc.ModalHeader(
            dbc.ModalTitle("Einstellungen"),
            close_button=False),
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
        dbc.ModalFooter([
            dbc.Checkbox(
                id="save-settings-checkbox",
                label="Einstellungen beibehalten"
            ),
            dbc.Button(
                "Speichern", id="settings-modal-save", className="ms-auto", n_clicks=0
            )
        ]),
    ],
    id="settings-modal",
    is_open=False,
    size="xl",
    backdrop="static",
)
