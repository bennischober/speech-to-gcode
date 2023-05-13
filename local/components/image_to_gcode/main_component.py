from dash import html, callback, no_update
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import numpy as np
import cv2
import base64

from components.image_to_gcode.converter import image_to_gcode
from components.image_to_gcode.dynamic_layout import gcode_state_success_layout, gcode_state_error_layout, gcode_content_layout

def get_image_to_gcode_component():
    return dbc.Card(
        children=[
            dbc.CardHeader('Image to GCode'),
            html.Div(id='test'),

            dbc.CardBody([
                html.Div([], id='gcode_state_layout'),
                html.Div([], id='gcode_content_layout')
            ]),
        ],
        className='mb-4',
        style={
            'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
            'text-align': 'center',
            'margin': ' 25px auto',
        })

### Show GCODE if button is clicked ###
@callback(
    Output("show_gcode", "is_open"),
    [Input("show_gcode_button", "n_clicks")],
    [State("show_gcode", "is_open")],
)
def toggle_collapse1(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

@callback(
    Output('gcode_store', 'data'),
    State('base64_selected_stable_diff_img_store', 'data'),
    Input('base64_dilated_image_store', 'data'),
    prevent_initial_call=True
)
def update_code_list(org_base64, dilated_base64):
    # Convert base64 img to cv mat
    decoded_image = base64.b64decode(org_base64.split(',')[1])
    image_array = np.frombuffer(decoded_image, dtype=np.uint8)
    org = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    dilated_decoded_image = base64.b64decode(dilated_base64.split(',')[1])
    dilated_image_array = np.frombuffer(dilated_decoded_image, dtype=np.uint8)
    dilated = cv2.imdecode(dilated_image_array, cv2.IMREAD_GRAYSCALE)

    gcode_data = None
    if dilated is not None and org is not None:
        gcode_data = image_to_gcode(dilated)

    return gcode_data

@callback(
    Output('gcode_state_layout', 'children'),
    Output('recent_gcode_generated_successfully_store', 'data'),
    State('recent_gcode_generated_successfully_store', 'data'),
    Input('gcode_store', 'data'),
    prevent_initial_call=True
)
def display_gcode_state_layout(recent_gcode_generated_successfully, gcode_data):
    current_gcode_generated_successfully = True if gcode_data != None else False
    if current_gcode_generated_successfully == recent_gcode_generated_successfully:
        return no_update
    
    gcode_state_layout = gcode_state_success_layout if gcode_data != None else gcode_state_error_layout
    return gcode_state_layout, current_gcode_generated_successfully

@callback(
    Output('gcode_content_layout', 'children'),
    State('recent_gcode_generated_successfully_store', 'data'),
    Input('gcode_store', 'data'),
    prevent_initial_call=True
)
def load_gcode_content_layout(recent_gcode_generated_successfully, gcode_data):

    current_gcode_generated_successfully = True if gcode_data != None else False
    if current_gcode_generated_successfully == False:
        return []

    if current_gcode_generated_successfully == recent_gcode_generated_successfully:
        return no_update
    
    return gcode_content_layout

@callback(
    Output('gcode_visualization', 'children'),
    State('gcode_store', 'data'),
    Input('gcode_content_layout', 'children')
)
def load_gcode(gcode_data, gcode_content_layout):
    if gcode_content_layout == []:
        return no_update
    
    return ''.join(gcode_data)
