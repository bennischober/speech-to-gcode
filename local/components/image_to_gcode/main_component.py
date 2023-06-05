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
                            dbc.Card([
                                dbc.CardHeader(
                                    dbc.Button(
                                        "GCODE Statistik",
                                        id="show_gcode_statistics_button",
                                        color="link",
                                        className="btn btn-link text-left h3",
                                        style={
                                            'color': 'white',
                                            'font-size': '24px'
                                        }
                                    )
                                ),
                                dbc.Collapse(
                                    [
                                        dbc.CardBody(
                                            [
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
                                            ]
                                        )
                                    ],
                                    id="gcode_statistic_collapse",
                                    is_open=True
                                )
                            ], style={'margin': '0 0 20px 0'}),
                            dbc.Card([
                                dbc.CardHeader(
                                    dbc.Button(
                                        "GCODE Parameter",
                                        id="show_gcode_params_button",
                                        color="link",
                                        className="btn btn-link text-left h3",
                                        style={
                                            'color': 'white',
                                            'font-size': '24px'
                                        }
                                    )
                                ),
                                dbc.Collapse(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.Div(
                                                    children=[
                                                        html.Div([
                                                            html.Label('Epsilon:'),
                                                            html.Div([
                                                                dcc.Slider(
                                                                    id='edge_approx_epsilon_slider',
                                                                    min=0.0,
                                                                    max=5.0,
                                                                    step=0.1,
                                                                    value=0.0,
                                                                    marks={i/10 if (i / 10) % 1 != 0 else int(i/10): str(i/10) for i in range(0, 51, 5)}
                                                                ),
                                                            ], style={'width': '100%'}),
                                                        ], className='gcode_param_div'),
                                                        html.Div([
                                                            html.Label('GCODE Größe (mm):', className='gcode_param_label'),
                                                            dcc.Input(
                                                                id='gcode_size',
                                                                type='number',
                                                                step=1,
                                                                value=210, 
                                                                style={'width': '100px'}
                                                            ),
                                                        ], className='gcode_param_div'),
                                                        html.Div([
                                                            html.Label('Min Konturen Länge:', className='gcode_param_label'),
                                                            dcc.Input(
                                                                id='min_contour_len',
                                                                type='number',
                                                                step=1,
                                                                value=15,
                                                                style={'width': '100px'}
                                                            ),
                                                        ], className='gcode_param_div'),
                                                        html.Div([
                                                            html.Label('Blurr Kernel Größe:', className='gcode_param_label'),
                                                            dcc.Input(
                                                                id='blurr_kernel_size',
                                                                type='number',
                                                                step=1,
                                                                value=5, 
                                                                min=1,
                                                                style={'width': '100px'}
                                                            ),
                                                        ], className='gcode_param_div'),
                                                        html.Div([
                                                            html.Label('Z sichere Höhe:', className='gcode_param_label'),
                                                            dcc.Input(
                                                                id='z_safe_hight',
                                                                type='number',
                                                                step=0.01,
                                                                value=10.0, 
                                                                style={'width': '100px'}
                                                            ),
                                                        ], className='gcode_param_div'),
                                                        html.Div([
                                                            html.Label('Z Arbeits-Höhe:', className='gcode_param_label'),
                                                            dcc.Input(
                                                                id='z_working_hight',
                                                                type='number',
                                                                step=0.01,
                                                                value=1.5, 
                                                                style={'width': '100px'}
                                                            ),
                                                        ], className='gcode_param_div'),
                                                        html.Div([
                                                            html.Label('Z Null-Höhe:', className='gcode_param_label'),
                                                            dcc.Input(
                                                                id='z_zero_height',
                                                                type='number',
                                                                step=0.001,
                                                                value=0.1, 
                                                                style={'width': '100px'}
                                                            ),
                                                        ], className='gcode_param_div'),
                                                        html.Div([
                                                            html.Label('Z Fräs-Höhe:', className='gcode_param_label'),
                                                            dcc.Input(
                                                                id='z_feed_height',
                                                                type='number',
                                                                step=0.001,
                                                                value=0.0, 
                                                                style={'width': '100px'}
                                                            ),
                                                        ], className='gcode_param_div'),
                                                        html.Div([
                                                            html.Label('Z Vorschub:', className='gcode_param_label'),
                                                            dcc.Input(
                                                                id='z_feed',
                                                                type='number',
                                                                step=10,
                                                                value=500, 
                                                                style={'width': '100px'}
                                                            ),
                                                        ], className='gcode_param_div'),
                                                        html.Div([
                                                            html.Label('XY Vorschub:', className='gcode_param_label'),
                                                            dcc.Input(
                                                                id='xy_feed',
                                                                type='number',
                                                                step=10,
                                                                value=1000, 
                                                                style={'width': '100px'}
                                                            ),
                                                        ], className='gcode_param_div'),
                                                        html.Div([
                                                            html.Label('Drehgeschwindigkeit:', className='gcode_param_label'),
                                                            dcc.Input(
                                                                id='spindle_speed',
                                                                type='number',
                                                                step=10,
                                                                value=24000, 
                                                                style={'width': '100px'}
                                                            ),
                                                        ], className='Max gcode_param_div'),
                                                        html.Div([
                                                            html.Label('Max Vorschub:', className='gcode_param_label'),
                                                            dcc.Input(
                                                                id='g0_feed',
                                                                type='number',
                                                                step=1,
                                                                value=2300, 
                                                                style={'width': '100px'}
                                                            ),
                                                        ], className='gcode_param_div'),
                                                    ]
                                                )
                                            ]
                                        )
                                    ],
                                    id="gcode_params_collapse",
                                    is_open=False
                                )
                            ], style={'margin': '0 0 20px 0'}),
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
                html.Div([
                    html.Div([
                            dbc.Button("GCODE Kopieren", id="copy_gcode_button", color="primary", className="mr-2")
                        ]
                    ),
                    dbc.Button("Hier Klicken, um den Code anzuzeigen", id="show_gcode_button", className="mt-3 show_gcode_button"),
                    dbc.Collapse([
                        html.H6("G-Code:"),
                        dbc.CardBody([
                            html.Pre(
                                id='gcode_visualization', children=[], className='gcode_style')
                        ]),
                    ], style={'background': '#ffffff', 'margin': 'auto', 'width': '60vw'}, id="show_gcode", is_open=False)
                ])
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

# Show GCODE Statistics
@callback(
    Output("gcode_statistic_collapse", "is_open", allow_duplicate=True),
    Output("gcode_params_collapse", "is_open", allow_duplicate=True),
    [Input("show_gcode_statistics_button", "n_clicks")],
    [State("gcode_statistic_collapse", "is_open")],
    [State("gcode_params_collapse", "is_open")],
    prevent_initial_call=True
)
def toggle_collapse(n_clicks, stats_is_open, params_is_open):
    if n_clicks:
        return not stats_is_open, False if not stats_is_open else params_is_open
    
    return stats_is_open, params_is_open

# Show GCODE Params
@callback(
    Output("gcode_params_collapse", "is_open", allow_duplicate=True),
    Output("gcode_statistic_collapse", "is_open", allow_duplicate=True),
    [Input("show_gcode_params_button", "n_clicks")],
    [State("gcode_params_collapse", "is_open")],
    [State("gcode_statistic_collapse", "is_open")],
    prevent_initial_call=True
)
def toggle_collapse(n_clicks, params_is_open, stats_is_open):
    if n_clicks:
        return not params_is_open, False if not params_is_open else stats_is_open
    
    return params_is_open, stats_is_open

@callback(
    Output('gcode_store', 'data'),
    Output('ordered_contours_store', 'data'),
    Output('gcode_stats_store', 'data'),
    Input('base64_edge_image_store', 'data'),
    Input('edge_approx_epsilon_slider', 'value'),
    Input('gcode_size', 'value'),
    Input('min_contour_len', 'value'),
    Input('blurr_kernel_size', 'value'),
    Input('z_safe_hight', 'value'),
    Input('z_working_hight', 'value'),
    Input('z_zero_height', 'value'),
    Input('z_feed_height', 'value'),
    Input('z_feed', 'value'),
    Input('xy_feed', 'value'),
    Input('spindle_speed', 'value'),
    Input('g0_feed', 'value'),
    prevent_initial_call=True
)
def update_code_list(edge_base64, epsilon, gcode_size, min_contour_len, blurr_kernel_size, z_safe_hight, z_working_hight, 
                     z_zero_height, z_feed_height, z_feed, xy_feed, spindle_speed, g0_feed):
    edge_decoded_image = base64.b64decode(edge_base64.split(',')[1])
    edge_image_array = np.frombuffer(edge_decoded_image, dtype=np.uint8)
    edge_image = cv2.imdecode(edge_image_array, cv2.IMREAD_GRAYSCALE)

    image_size = 720
    params = {
        'epsilon': epsilon,
        'gcode_size': gcode_size,
        'min_contour_len': min_contour_len,
        'blurr_kernel_size': blurr_kernel_size,
        'z_safe_hight': z_safe_hight,
        'z_working_hight': z_working_hight,
        'z_zero_height': z_zero_height,
        'z_feed_height': z_feed_height,
        'z_feed': z_feed,
        'xy_feed': xy_feed,
        'g0_feed': g0_feed,
        'spindle_speed': spindle_speed,
        'resize_factor': gcode_size / image_size,
        'start_point': np.array([0, 0])
    }

    gcode_data = None; ordered_contours = None; gcode_stats = None
    if edge_image is not None:
        gcode_data, ordered_contours, gcode_stats = image_to_gcode(edge_image, params)
        
    return gcode_data, ordered_contours, gcode_stats

@callback(
    Output('gcode_visualization', 'children'),
    Input('gcode_store', 'data')
)
def load_gcode(gcode_data):
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
