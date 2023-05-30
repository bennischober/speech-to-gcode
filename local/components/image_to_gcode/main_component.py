from dash import html, callback, no_update, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import numpy as np
import cv2
import base64
import pyperclip
import matplotlib.pyplot as plt
import io

from components.image_to_gcode.converter import image_to_gcode
from components.image_to_gcode.dynamic_layout import gcode_content_layout

def get_image_to_gcode_component():
    return dbc.Card(
        children=[
            dbc.CardHeader('Image to GCode'),

            dbc.CardBody([
                html.Div([
                    html.Div(
                        children=[
                            html.H3('Status'),
                            html.Div([
                                html.H1("00:00:00", id='total_feeding_time', style={"font-size": "48px","margin-bottom": "10px","color": "#007bff"}),
                                html.P("Gesamt-Fräszeit", style={"font-size": "18px", "color": "#6c757d"}),
                            ], style={"margin": "30px 0 30px 0"}),
                            html.Table(
                                [
                                    # html.Tr([html.Td(html.Strong("Fräßzeit:")), html.Td('00:00:00', id="fräzeit", style={"font-weight": "bold", "color": "purple", 'padding': '5px 5px 5px 15px'})]),
                                    html.Tr([html.Td(html.Strong("Konturenanzahl:")), html.Td('0', id="amt_contours", style={"font-weight": "bold", "color": "#BF40BF", 'padding': '5px 5px 5px 15px'})]),
                                    html.Tr([html.Td(html.Strong("GCODE-Zeilenanzahl:")), html.Td('0', id="amt_gcode_lines", style={"font-weight": "bold", "color": "#BF40BF", 'padding': '5px 5px 5px 15px'})]),
                                    html.Tr([html.Td(html.Strong("G0-xy-Distanz:")), html.Td('0', id="g0_xy_distance", style={"font-weight": "bold", "color": "#BF40BF", 'padding': '5px 5px 5px 15px'})]),
                                    html.Tr([html.Td(html.Strong("G0-z-Distanz:")), html.Td('0', id="g0_z_distance", style={"font-weight": "bold", "color": "#BF40BF", 'padding': '5px 5px 5px 15px'})]),
                                    html.Tr([html.Td(html.Strong("G0 Fräszeit:")), html.Td('0', id="g0_feeding_time", style={"font-weight": "bold", "color": "#BF40BF", 'padding': '5px 5px 5px 15px'})]),
                                    html.Tr([html.Td(html.Strong("G1-xy-Distanz:")), html.Td('0', id="g1_xy_distance", style={"font-weight": "bold", "color": "#BF40BF", 'padding': '5px 5px 5px 15px'})]),
                                    html.Tr([html.Td(html.Strong("G1-z-Distanz:")), html.Td('0', id="g1_z_distance", style={"font-weight": "bold", "color": "#BF40BF", 'padding': '5px 5px 5px 15px'})]),
                                    html.Tr([html.Td(html.Strong("G1 Fräszeit:")), html.Td('0', id="g1_feeding_time", style={"font-weight": "bold", "color": "#BF40BF", 'padding': '5px 5px 5px 15px'})]),
                                ],
                                id="output-table",
                                className="table",
                                style={"text-align": "left", "font-size": "120%"}
                            ),
                            html.H3('Parameter'),
                            html.Div(
                                children=[
                                    html.Label('Epsilon'),
                                    dcc.Slider(
                                        id='edge_approx_epsilon_slider',
                                        min=0.0,
                                        max=4.0,
                                        step=0.1,
                                        value=0.0,
                                        marks={i/10 if (i / 10) % 1 != 0 else int(i/10): str(i/10) for i in range(0, 41, 5)}
                                    ),
                                    html.Div(id='slider-output')
                                ]
                            )
                        ],
                        style={'flex': '30%', 'padding': '20px'},
                    ),
                    html.Div(
                        style={'flex': '70%', 'padding': '20px'},
                        children=[
                            html.H3('GCODE Bild'),
                            dcc.Loading(
                                id='loading-icon',
                                type='default',
                                children=[
                                    html.Img(id='gcode_image', className='img-thumbnail')
                                ]
                            )
                        ]
                    )
                ], style={'display': 'flex'}),
                html.Div(gcode_content_layout, id='gcode_content_layout')
            ]),
        ],
        className='mb-4 card_image_to_gcode')

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
    Output('ordered_contours_store', 'data'),
    Output('gcode_stats_store', 'data'),
    Input('base64_edge_image_store', 'data'),
    Input('edge_approx_epsilon_slider', 'value'),
    prevent_initial_call=True
)
def update_code_list(edge_base64, epsilon):
    edge_decoded_image = base64.b64decode(edge_base64.split(',')[1])
    edge_image_array = np.frombuffer(edge_decoded_image, dtype=np.uint8)
    edge_image = cv2.imdecode(edge_image_array, cv2.IMREAD_GRAYSCALE)

    params = {'epsilon': epsilon}

    gcode_data = None; ordered_contours = None; gcode_stats = None
    if edge_image is not None:
        gcode_data, ordered_contours, gcode_stats = image_to_gcode(edge_image, params)
        
    return gcode_data, ordered_contours, gcode_stats

@callback(
    Output('gcode_visualization', 'children'),
    State('gcode_store', 'data'),
    Input('gcode_content_layout', 'children')
)
def load_gcode(gcode_data, gcode_content_layout):
    if gcode_content_layout == []:
        return no_update
    
    return gcode_data

@callback(
    Output("copy_gcode_button", "n_clicks"),
    State("gcode_store", "data"),
    Input("copy_gcode_button", "n_clicks")
)
def copy_to_clipboard(gcode, n_clicks):
    if n_clicks is not None and n_clicks > 0:
        pyperclip.copy(gcode)
    
    return n_clicks

@callback(
    Output("total_feeding_time", "children"),
    Output("amt_contours", "children"),
    Output("amt_gcode_lines", "children"),
    Output("g0_xy_distance", "children"),
    Output("g0_z_distance", "children"),
    Output("g0_feeding_time", "children"),
    Output("g1_xy_distance", "children"),
    Output("g1_z_distance", "children"),
    Output("g1_feeding_time", "children"),
    Input("gcode_stats_store", "data")
)
def display_gcode_stats(gcode_stats):
    return \
        gcode_stats['total_feeding_time'], \
        gcode_stats['amt_contours'], \
        gcode_stats['amt_gcode_lines'], \
        gcode_stats['g0_xy_distance'], \
        gcode_stats['g0_z_distance'], \
        gcode_stats['g0_feeding_time'], \
        gcode_stats['g1_xy_distance'], \
        gcode_stats['g1_z_distance'], \
        gcode_stats['g1_feeding_time']

@callback(
    Output('gcode_image', 'src'),
    Input('ordered_contours_store', 'data'),
    prevent_initial_call=True
)
def display_gcode_image(ordered_contours):
    plt.close()

    fig = plt.figure(figsize=( 512 / 50, 512 / 50))
    fig.patch.set_facecolor('black')

    doubled_lines = []

    for contour in ordered_contours:
        contour = np.array(contour)
        x_approx = contour[:, :, 0].flatten()
        y_approx = contour[:, :, 1].flatten()

        plt.plot(x_approx, y_approx, color='blue')

    plt.gca().invert_yaxis()
    plt.axis('off')

    # Erstelle einen Bytes-Puffer
    buffer = io.BytesIO()

    # Speichere das Plot-Diagramm im Puffer
    plt.savefig(buffer, format='png', bbox_inches='tight')

    # Setze die Position des Puffers auf den Anfang
    buffer.seek(0)

    # Konvertiere das Plot-Diagramm in einen Base64-codierten String
    plot_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    # Schließe das Plot-Diagramm
    plt.close()

    return f"data:image/png;base64,{plot_base64}"
