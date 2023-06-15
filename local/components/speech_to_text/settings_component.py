import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, State, ctx
from utils.config import POSITIVE_PROMPTS, NEGATIVE_PROMPTS


def _create_tabs(prefix: str):
    return dbc.Tab([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H6(f"{prefix.capitalize()} Prompts"),
                    dbc.Checklist(id=f"{prefix}-prompts-checklist"),
                ], lg=5),
                dbc.Col([
                    dbc.InputGroup([
                        dbc.Input(id=f"{prefix}-prompts-input", type="text",
                                  placeholder=f"Optional: Geben Sie einen {prefix}n Prompt ein"),
                        dbc.Button(id=f"add-{prefix}-prompt",
                                   children="Hinzufügen", n_clicks=0),
                        dbc.Button(
                            id=f"select-all-{prefix}-prompts", children="Alles auswählen", n_clicks=0, color="secondary"),
                    ]),
                ], lg=7),
            ]),
        ],
            className="m-3"
        ),
    ], label=f"{prefix.capitalize()} Prompts", tab_id=prefix)


def _create_callbacks(prefix: str, initial_items):
    @callback(
        Output(f"{prefix}-prompts-checklist", "options"),
        Output(f"{prefix}-prompts-checklist", "value"),
        Output(f"{prefix}-all-prompts-store", "data"),
        Output(f"{prefix}-selected-prompts-store", "data"),
        Output(f"{prefix}-prompts-input", "value"),
        Output(f"select-all-{prefix}-prompts", "children"),
        Input(f"add-{prefix}-prompt", "n_clicks"),
        Input(f"{prefix}-all-prompts-store", "data"),
        Input(f"{prefix}-selected-prompts-store", "data"),
        Input(f"{prefix}-prompts-checklist", "value"),
        Input(f"select-all-{prefix}-prompts", "n_clicks"),
        Input("reset-inputs", "n_clicks"),
        State(f"{prefix}-prompts-input", "value"),
        prevent_initial_call=True,
    )
    def update_prompts(n_clicks, all_prompts, selected_prompts, checklist_value, select_all_clicks, reset_clicks, input_value):
        triggered_id = ctx.triggered_id

        if all_prompts is None:
            all_prompts = initial_items[:]

        if selected_prompts is None:
            selected_prompts = initial_items[:]

        if triggered_id == f"add-{prefix}-prompt" and input_value and input_value not in all_prompts:
            all_prompts.append(input_value)
            selected_prompts.append(input_value)
            input_value = None

        if checklist_value is not None:
            selected_prompts = checklist_value

        button_text = "Alles selektieren"
        if set(selected_prompts) == set(all_prompts):
            button_text = "Alles deselektieren"
            

        if triggered_id == f"select-all-{prefix}-prompts":
            # If all prompts are selected, deselect them
            if set(selected_prompts) == set(all_prompts):
                selected_prompts = []
                button_text = "Alles selektieren"
            # If not all prompts are selected, select them
            else:
                selected_prompts = all_prompts[:]
                button_text = "Alles deselektieren"

        if triggered_id == "reset-inputs":
            all_prompts = initial_items[:]
            selected_prompts = initial_items[:]
            input_value = None

        options = [{"label": prompt, "value": prompt}
                   for prompt in all_prompts]

        return options, selected_prompts, all_prompts, selected_prompts, input_value, button_text

    return update_prompts


_create_callbacks("positive", POSITIVE_PROMPTS)
_create_callbacks("negative", NEGATIVE_PROMPTS)


@callback(
    Output("settings-modal", "is_open"),
    Output("positive-all-prompts-store", "data", allow_duplicate=True),
    Output("negative-all-prompts-store", "data", allow_duplicate=True),
    Output("positive-selected-prompts-store", "data", allow_duplicate=True),
    Output("negative-selected-prompts-store", "data", allow_duplicate=True),
    Input("settings-modal-open", "n_clicks"),
    Input("settings-modal-save", "n_clicks"),
    State("settings-modal", "is_open"),
    State("save-settings-checkbox", "value"),
    State("positive-all-prompts-store", "data"),
    State("negative-all-prompts-store", "data"),
    State("positive-selected-prompts-store", "data"),
    State("negative-selected-prompts-store", "data"),
    prevent_initial_call=True
)
def toggle_modal(n1, n2, is_open, save, positive_all, negative_all, positive_selected, negative_selected):
    if n1 or n2:
        new_is_open = not is_open
        if not new_is_open and not save:  # reset stores to initial state if the modal is being closed and the settings shouldn't be saved
            positive_all = POSITIVE_PROMPTS[:]
            negative_all = NEGATIVE_PROMPTS[:]
            positive_selected = POSITIVE_PROMPTS[:]
            negative_selected = NEGATIVE_PROMPTS[:]
        return new_is_open, positive_all, negative_all, positive_selected, negative_selected
    return is_open, positive_all, negative_all, positive_selected, negative_selected


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
