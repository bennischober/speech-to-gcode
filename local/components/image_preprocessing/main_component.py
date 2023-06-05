import dash_bootstrap_components as dbc
from dash import html, Input, Output, callback, dcc
import cv2
import base64
import numpy as np
from components.image_to_gcode.params import blurr_kernel_size

dilated_img = None
orginal_img = None 

def get_image_preprocessing_component():
    return dbc.Card(
            children=[
                dbc.CardHeader('Image Preprocessing'),
                dbc.Row([
                    dbc.Col([
                        html.H4('Eingabe', id='testA'),
                        html.Img(id='origial-image', className='img-thumbnail center_image')
                    ], className='image_preprocessing'),
                    dbc.Col([
                        html.H4('Graustufenbild'),
                        html.Img(id='gray-image', className='img-thumbnail center_image')
                    ]),
                    dbc.Col([
                        html.H4('Blurred-Bild'),
                        html.Img(id='blurred-image', className='img-thumbnail center_image')
                    ]),
                    dbc.Col([
                        html.H4('Kantenbild'),
                        html.Img(id='edges-image', className='img-thumbnail center_image')
                    ]),
                ], className='m-4 row_with_images'),
            ]
        )

@callback(
          Output('origial-image', 'src'),
          Output('gray-image', 'src'),
          Output('blurred-image', 'src'),
          Output('edges-image', 'src'),
          Output('base64_edge_image_store', 'data'),
          Input('base64_selected_stable_diff_img_store', 'data'))
def process_image(selected_diff_image):
    if selected_diff_image is not None:
        # Convert image
        decoded_image = base64.b64decode(selected_diff_image.split(',')[1])
        image_array = np.frombuffer(decoded_image, dtype=np.uint8)
        origial = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        # origial = cv2.imread("components/image_preprocessing/elefant.jpeg")
        _, origial_encoded = cv2.imencode('.png', origial)
        original_base64 = base64.b64encode(origial_encoded).decode('utf-8')


        # Graustufenbild
        gray = cv2.cvtColor(origial, cv2.COLOR_BGR2GRAY)
        _, gray_encoded = cv2.imencode('.png', gray)
        gray_base64 = base64.b64encode(gray_encoded).decode('utf-8')

        # Rauschen eliminieren
        blurred =  cv2.GaussianBlur(gray, (blurr_kernel_size, blurr_kernel_size), 0)
        _, blurred_encoded = cv2.imencode('.png', blurred)
        blurred_base64 = base64.b64encode(blurred_encoded).decode('utf-8')

        # Canny-Kanten-Detektor
        edges = cv2.Canny(blurred, 100, 200)
        _, edges_encoded = cv2.imencode('.png', edges)
        edges_base64 = base64.b64encode(edges_encoded).decode('utf-8')

        return f"data:image/png;base64,{original_base64}", \
            f"data:image/png;base64,{gray_base64}", \
            f"data:image/png;base64,{blurred_base64}", \
            f"data:image/png;base64,{edges_base64}", \
            f"data:image/png;base64,{edges_base64}"