from dash import dash, html, callback, Input, Output, dcc, State
import dash_bootstrap_components as dbc
import requests
import zipfile
import base64
import io
from utils.config import SD_ENDPOINT

preloaded_images = None
with open("components/stable_diffusion/preloaded_images.txt", "r") as file:
    preloaded_images = eval(file.read())


def get_stable_diffusion_component():
    return dbc.Card(
        children=[
            dbc.CardHeader('Stable Diffusion'),
            dbc.Row([
                dbc.Col([
                    html.H4('Bild 1', style={"textAlign": "center"}),
                    dcc.Loading(
                        dbc.Button(
                            html.Img(id='stable_diff_img_1', className='img-thumbnail', src=preloaded_images[0],
                                     style={"display": "block", "margin": "auto"}),
                            id='button_diff_img_1')
                    )
                ]),
                dbc.Col([
                    html.H4('Bild 2', style={"textAlign": "center"}),
                    dcc.Loading(
                        dbc.Button(
                            html.Img(id='stable_diff_img_2', className='img-thumbnail', src=preloaded_images[1],
                                     style={"display": "block", "margin": "auto"}),
                            id='button_diff_img_2')
                    )
                ]),
                dbc.Col([
                    html.H4('Bild 3', style={"textAlign": "center"}),
                    dcc.Loading(
                        dbc.Button(
                            html.Img(id='stable_diff_img_3', className='img-thumbnail', src=preloaded_images[2],
                                     style={"display": "block", "margin": "auto"}),
                            id='button_diff_img_3')
                    )
                ]),
                dbc.Col([
                    html.H4('Bild 4', style={"textAlign": "center"}),
                    dcc.Loading(
                        dbc.Button(
                            html.Img(id='stable_diff_img_4', className='img-thumbnail', src=preloaded_images[3],
                                     style={"display": "block", "margin": "auto"}),
                            id='button_diff_img_4')
                    )
                ], className='mb-3', style={'padding': '0px 5px 5px 0px'}),
            ]),
            dbc.Button("Bilder neu laden", id='generate_diff_imges',
                       className='mb-3', style={'padding': '0px 5px 5px 0px'}),
        ],
        className='mb-4',
        style={
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
        }
    )

def get_selected_preload_image():
    return preloaded_images[0]

# Callback to extract images from ZIP file and store in base64 format
@callback(
    Output('stable_diff_img_1', 'src'),
    Output('stable_diff_img_2', 'src'),
    Output('stable_diff_img_3', 'src'),
    Output('stable_diff_img_4', 'src'),
    Input('diffusion_prompt', 'data'),
    Input('generate_diff_imges', 'n_clicks')
)
def generate_diff_images(diffusion_prompt: dict, n_clicks: int):
    if n_clicks is None and diffusion_prompt is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Define the API endpoint
    url = SD_ENDPOINT

    data = {
        "prompt": diffusion_prompt['prompt'],
        "negative_prompt": diffusion_prompt['negative'],
        "num_images_per_prompt": 4
    }

    # Send the API request
    response = requests.post(url, json=data)

    # Extract images from ZIP file and store in base64 format
    image_stores = []
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        for i in range(4):
            image_name = f'image_{i}.jpg'
            with zip_file.open(image_name) as image_file:
                image_bytes = image_file.read()
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                image_stores.append(image_base64)

    return f"data:image/png;base64,{image_stores[0]}", \
           f"data:image/png;base64,{image_stores[1]}", \
           f"data:image/png;base64,{image_stores[2]}", \
           f"data:image/png;base64,{image_stores[3]}"


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
