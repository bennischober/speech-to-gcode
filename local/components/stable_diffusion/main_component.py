from dash import dash, html, callback, Input, Output, dcc, State
import dash_bootstrap_components as dbc
import requests
import zipfile
import base64
import io
import os
from utils.config import SD_ENDPOINT

import json

preloaded_images = None
with open(os.path.join(os.path.dirname(__file__), "preloaded_images.txt"), "r") as file:
    preloaded_images = eval(file.read())


def get_stable_diffusion_component():
    return dbc.Card(
        children=[
            dcc.Store(id='ratings-store', storage_type='session', data=None),
            html.Div(id='image-response-status', style={'display': 'none'}),
            dbc.CardHeader('Stable Diffusion'),
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.H4('Bild 1', style={"textAlign": "center"}),
                        dcc.Loading(
                            dbc.Button(
                                html.Img(
                                    id='stable_diff_img_1', className='img-thumbnail center_image', src=preloaded_images[0]),
                                id='button_diff_img_1', className='clickable_image_button')
                        ),
                        dbc.Row(
                            dbc.Col([
                                html.Span("i", id="info-icon_1", className="info-icon"),
                                dbc.Tooltip(
                                    id="tooltip_1",
                                    target="info-icon_1",
                                    placement="bottom",
                                ),
                            ],
                            className="center-container"
                            )
                        ),
                    ]),
                    dbc.Col([
                        html.H4('Bild 2', style={"textAlign": "center"}),
                        dcc.Loading(
                            dbc.Button(
                                html.Img(
                                    id='stable_diff_img_2', className='img-thumbnail center_image', src=preloaded_images[1]),
                                id='button_diff_img_2', className='clickable_image_button')
                        ),
                        dbc.Row(
                            dbc.Col([
                                html.Span("i", id="info-icon_2", className="info-icon"),
                                dbc.Tooltip(
                                    id="tooltip_2",
                                    target="info-icon_2",
                                    placement="bottom",
                                ),
                            ],
                            className="center-container"
                            )
                        ),
                    ]),
                    dbc.Col([
                        html.H4('Bild 3', style={"textAlign": "center"}),
                        dcc.Loading(
                            dbc.Button(
                                html.Img(
                                    id='stable_diff_img_3', className='img-thumbnail center_image', src=preloaded_images[2]),
                                id='button_diff_img_3', className='clickable_image_button')
                        ),
                        dbc.Row(
                            dbc.Col([
                                html.Span("i", id="info-icon_3", className="info-icon"),
                                dbc.Tooltip(
                                    id="tooltip_3",
                                    target="info-icon_3",
                                    placement="bottom",
                                ),
                            ],
                            className="center-container"
                            )
                        ),
                    ]),
                    dbc.Col([
                        html.H4('Bild 4', style={"textAlign": "center"}),
                        dcc.Loading(
                            dbc.Button(
                                html.Img(
                                    id='stable_diff_img_4', className='img-thumbnail center_image', src=preloaded_images[3]),
                                id='button_diff_img_4', className='clickable_image_button')
                        ),
                        dbc.Row(
                            dbc.Col([
                                html.Span("i", id="info-icon_4", className="info-icon"),
                                dbc.Tooltip(
                                    id="tooltip_4",
                                    target="info-icon_4",
                                    placement="bottom",
                                ),
                            ],
                            className="center-container"
                            )
                        ),
                    ]),
                ]),
                dbc.Button("Bilder neu laden",
                           id='generate_diff_imges', className="mt-3"),
            ], style={'width': '100%', 'padding': '20px 20px 20px 20px'}),
        ],
        className='mb-4'
    )


def get_selected_preload_image():
    return preloaded_images[0]

# Callback to extract images from ZIP file and store in base64 format
@callback(
    Output('stable_diff_img_1', 'src'),
    Output('stable_diff_img_2', 'src'),
    Output('stable_diff_img_3', 'src'),
    Output('stable_diff_img_4', 'src'),
    Output('ratings-store', 'data'),
    Output('notification-toast', 'is_open', allow_duplicate=True),
    Output('image-response-status', 'children', allow_duplicate=True),
    Input('diffusion_prompt', 'data'),
    Input('generate_diff_imges', 'n_clicks'),
    prevent_initial_call=True
)
def generate_diff_images(diffusion_prompt: dict, n_clicks: int):
    if n_clicks is None and diffusion_prompt is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Define the API endpoint
    url = SD_ENDPOINT

    data = {
        "prompt": diffusion_prompt['prompt'],
        "negative_prompt": diffusion_prompt['negative'],
        "search_prompt": diffusion_prompt['search_prompt'],
    }

    # Send the API request
    try:
        response = requests.post(url, json=data)
    except requests.exceptions.ConnectionError:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, False, "error"

    # Extract images from ZIP file and store in base64 format
    image_stores = []
    ratings = {}
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        for i in range(4):
            image_name = f'image_{i}.jpg'
            with zip_file.open(image_name) as image_file:
                image_bytes = image_file.read()
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                image_stores.append(image_base64)
        
        # extract ratings
        with zip_file.open("ratings.json") as ratings_file:
            ratings = json.loads(ratings_file.read().decode('utf-8'))

    return f"data:image/png;base64,{image_stores[0]}", \
           f"data:image/png;base64,{image_stores[1]}", \
           f"data:image/png;base64,{image_stores[2]}", \
           f"data:image/png;base64,{image_stores[3]}", \
           ratings, False, 'ok'


@callback(
    [
        Output("tooltip_1", "children"),
        Output("tooltip_2", "children"),
        Output("tooltip_3", "children"),
        Output("tooltip_4", "children"),
    ],
    Input("ratings-store", "data")
)
def update_tooltips(ratings):
    if ratings is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    tooltips_contents = []
    for image_name in ["image_0.jpg", "image_1.jpg", "image_2.jpg", "image_3.jpg"]:
        image_ratings = ratings.get(image_name, {"laion": "N/A", "dino": "N/A", "result": "N/A"})

        tooltip_content = html.Div(
            [
                html.Div(["dino_score: ", html.Span(round(image_ratings['dino'], 2))]),
                html.Div(["laion_score: ", html.Span(round(image_ratings['laion'], 2))]),
                html.Div(["final_score: ", html.Span(round(image_ratings['result'], 2))]),
            ],
        )

        tooltips_contents.append(tooltip_content)

    return tooltips_contents

@callback(
    Output('notification-toast', 'header', allow_duplicate=True),
    Output('notification-toast', 'children', allow_duplicate=True),
    Output('notification-toast', 'icon', allow_duplicate=True),
    Output('notification-toast', 'is_open', allow_duplicate=True),
    Output('notification-toast', 'duration', allow_duplicate=True),
    Input("image-response-status", "children"),
    prevent_initial_call=True
)
def update_notification(status: str):
    if status == 'ok':
        return "Erfolgreich", [html.P("Bilder wurden erfolgreich generiert.", className="mb-0")], "success", True, 3000
    if status == 'error':
        return "Fehler", [html.P("Es ist ein Fehler aufgetreten.", className="mb-0")], "danger", True, 3000
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

@callback(Output('base64_selected_stable_diff_img_store', 'data', allow_duplicate=True),
          State('stable_diff_img_1', 'src'),
          Input('button_diff_img_1', 'n_clicks'),
          prevent_initial_call=True)
def select_diff_img_1(image_src, _):
    return image_src


@callback(Output('base64_selected_stable_diff_img_store', 'data', allow_duplicate=True),
          State('stable_diff_img_2', 'src'),
          Input('button_diff_img_2', 'n_clicks'),
          prevent_initial_call=True)
def select_diff_img_2(image_src, _):
    return image_src


@callback(Output('base64_selected_stable_diff_img_store', 'data', allow_duplicate=True),
          State('stable_diff_img_3', 'src'),
          Input('button_diff_img_3', 'n_clicks'),
          prevent_initial_call=True)
def select_diff_img_3(image_src, _):
    return image_src


@callback(Output('base64_selected_stable_diff_img_store', 'data', allow_duplicate=True),
          State('stable_diff_img_4', 'src'),
          Input('button_diff_img_4', 'n_clicks'),
          prevent_initial_call=True)
def select_diff_img_4(image_src, _):
    return image_src
