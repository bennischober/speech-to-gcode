import dash_bootstrap_components as dbc
from dash import html, Input, Output, callback
import cv2
import base64
import os

def get_image_preprocessing_component():
    return dbc.Card(
            children=[
                dbc.CardHeader('Image Preprocessing'),
                dbc.CardBody('Short Description'),
                # Hier fügen Sie Ihre dritte Komponente hinzu
                dbc.Row([
                    dbc.Col([
                        html.H4('Stable-Diffusion-Bild', style={"text-align": "center"}),
                        html.Img(id='origial-image', className='img-thumbnail', style={"display": "block", "margin": "auto"})
                    ]),
                    dbc.Col([
                        html.H4('Graustufenbild', style={"text-align": "center"}),
                        html.Img(id='gray-image', className='img-thumbnail', style={"display": "block", "margin": "auto"})
                    ]),
                    dbc.Col([
                        html.H4('Blurred-Bild', style={"text-align": "center"}),
                        html.Img(id='blurred-image', className='img-thumbnail', style={"display": "block", "margin": "auto"})
                    ]),
                    dbc.Col([
                        html.H4('Kantenbild', style={"text-align": "center"}),
                        html.Img(id='edges-image', className='img-thumbnail', style={"display": "block", "margin": "auto"})
                    ]),
                    dbc.Col([
                        html.H4('Angepasste Kantendicke', style={"text-align": "center"}),
                        html.Img(id='dilated-image', className='img-thumbnail', style={"display": "block", "margin": "auto"})
                    ]),
                ], className='m-4', style={'padding': '0px 5px 5px 0px'}),
                dbc.Row([
                    dbc.Col([
                        dbc.Button('Load Image', id='load_image', color='primary')
                    ], width=12)
                ])
            ],
            className='mb-4',
            style={
                'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
            }
        )

# @callback(Input('load_image', 'n_clicks'))
# def log(_):
#     print('!!!!!!!!')

@callback(
          Output('origial-image', 'src'),
          Output('gray-image', 'src'),
          Output('blurred-image', 'src'),
          Output('edges-image', 'src'),
          Output('dilated-image', 'src'),
          Input('load_image', 'n_clicks'))
def process_image(n_clicks):
    origial = cv2.imread(os.path.join(os.path.dirname(__file__), "./image_preprocessing/elefant.jpeg"))
    _, origial_encoded = cv2.imencode('.png', origial)
    original_base64 = base64.b64encode(origial_encoded).decode('utf-8')


    # Graustufenbild
    gray = cv2.cvtColor(origial, cv2.COLOR_BGR2GRAY)
    _, gray_encoded = cv2.imencode('.png', gray)
    gray_base64 = base64.b64encode(gray_encoded).decode('utf-8')

    # Rauschen eliminieren
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, blurred_encoded = cv2.imencode('.png', blurred)
    blurred_base64 = base64.b64encode(blurred_encoded).decode('utf-8')

    # Canny-Kanten-Detektor
    edges = cv2.Canny(blurred, 100, 200)
    _, edges_encoded = cv2.imencode('.png', edges)
    edges_base64 = base64.b64encode(edges_encoded).decode('utf-8')

    # Kantenbreite (4 Pixel)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated = cv2.dilate(edges, kernel)
    _, dilated_encoded = cv2.imencode('.png', dilated)
    dilated_base64 = base64.b64encode(dilated_encoded).decode('utf-8')

    return f"data:image/png;base64,{original_base64}", \
           f"data:image/png;base64,{gray_base64}", \
           f"data:image/png;base64,{blurred_base64}", \
           f"data:image/png;base64,{edges_base64}", \
           f"data:image/png;base64,{dilated_base64}"