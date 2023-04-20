from dash import dash, html, callback, Input, Output, dcc, State
import dash_bootstrap_components as dbc
import requests
import zipfile
import base64
import io

def get_stable_diffusion_component():
    return dbc.Card(
            children=[
                dbc.CardHeader('Stable Diffusion'),
                dbc.Container([
                    dbc.Row([
                        dbc.Col([
                            html.H4('Bild 1', style={"text-align": "center"}),
                            dcc.Loading(
                                dbc.Button(
                                    html.Img(id='stable_diff_img_1', className='img-thumbnail', style={"display": "block", "margin": "auto"}), 
                                id='button_diff_img_1')
                            )
                        ]),
                        dbc.Col([
                            html.H4('Bild 2', style={"text-align": "center"}),
                            dcc.Loading(
                                dbc.Button(
                                    html.Img(id='stable_diff_img_2', className='img-thumbnail', style={"display": "block", "margin": "auto"}), 
                                id='button_diff_img_2')
                            )
                        ]),
                        dbc.Col([
                            html.H4('Bild 3', style={"text-align": "center"}),
                            dcc.Loading(
                                dbc.Button(
                                    html.Img(id='stable_diff_img_3', className='img-thumbnail', style={"display": "block", "margin": "auto"}), 
                                id='button_diff_img_3')
                            )
                        ]),
                        dbc.Col([
                            html.H4('Bild 4', style={"text-align": "center"}),
                            dcc.Loading(
                                dbc.Button(
                                    html.Img(id='stable_diff_img_4', className='img-thumbnail', style={"display": "block", "margin": "auto"}), 
                                id='button_diff_img_4')
                            )
                        ]),
                    ], className='mb-3', style={'padding': '0px 5px 5px 0px'}),
                    # dcc.Store(id='stable_diff_img_1'),
                    # dcc.Store(id='stable_diff_img_2'),
                    # dcc.Store(id='stable_diff_img_3'),
                    # dcc.Store(id='stable_diff_img_4'),
                    dcc.Store(id='stable_diff_selected_img')
                ]),
                dbc.Button("Bilder neu laden", id='generate_diff_imges', className='mb-3', style={'padding': '0px 5px 5px 0px'}),
            ],
            className='mb-4',
            style={
                'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
            }
        )

# Callback to extract images from ZIP file and store in base64 format
@callback(
    Output('stable_diff_img_1', 'src'),
    Output('stable_diff_img_2', 'src'),
    Output('stable_diff_img_3', 'src'),
    Output('stable_diff_img_4', 'src'),
    Input('generate_diff_imges', 'n_clicks')
)
def generate_diff_images(n_clicks):
    if n_clicks is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Define the API endpoint
    url = "http://localhost:5000/stable_diff"

    # Define the prompt data
    # prompt: realistic digital portrait, global illumination, shot at 8k resolution, highly detailed, photo realistic, masterpiece
    # negative_prompt: bad art, low detail, plain background, grainy, low quality, disfigured, out of frame, bad proportions, distortion, deformations
    data = {
        "prompt": "Eine Katze mit Piratenhut",
        "negative_prompt": "",
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

@callback(Output('stable_diff_selected_img', 'data', allow_duplicate=True),
          State('stable_diff_img_1', 'src'),
          Input('button_diff_img_1', 'n_clicks'),
          prevent_initial_call=True)
def select_diff_img_1(image_src, _):
    return image_src

@callback(Output('stable_diff_selected_img', 'data', allow_duplicate=True),
          State('stable_diff_img_2', 'src'),
          Input('button_diff_img_2', 'n_clicks'),
          prevent_initial_call=True)
def select_diff_img_2(image_src, _):
    return image_src

@callback(Output('stable_diff_selected_img', 'data', allow_duplicate=True),
          State('stable_diff_img_3', 'src'),
          Input('button_diff_img_3', 'n_clicks'),
          prevent_initial_call=True)
def select_diff_img_3(image_src, _):
    return image_src

@callback(Output('stable_diff_selected_img', 'data', allow_duplicate=True),
          State('stable_diff_img_4', 'src'),
          Input('button_diff_img_4', 'n_clicks'),
          prevent_initial_call=True)
def select_diff_img_4(image_src, _):
    return image_src