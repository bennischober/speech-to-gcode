from dash import callback

from dash.dependencies import Input, Output, State
import numpy as np
import cv2
import base64
import pyperclip
import matplotlib.pyplot as plt
import io

from components.image_to_gcode.converter import image_to_gcode
from components.image_to_gcode.layout import layout
from components.image_to_gcode.milling_grbl.studenten import Application

def get_image_to_gcode_component():
    return layout

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
    Output('dynamic_params', 'data'),
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
def changeDynamicParams(epsilon, gcode_size, min_contour_len, blurr_kernel_size, z_safe_hight, 
                        z_working_hight, z_zero_height, z_feed_height, z_feed, xy_feed, spindle_speed, 
                        g0_feed):

    return {
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
        'spindle_speed': spindle_speed,
        'g0_feed': g0_feed
    }

@callback(
    Output('gcode_store', 'data'),
    Output('ordered_contours_store', 'data'),
    Output('gcode_stats_store', 'data'),
    Input('base64_edge_image_store', 'data'),
    State('dynamic_params', 'data'),
    prevent_initial_call=True
)
def update_code_list(edge_base64, params):
    edge_decoded_image = base64.b64decode(edge_base64.split(',')[1])
    edge_image_array = np.frombuffer(edge_decoded_image, dtype=np.uint8)
    edge_image = cv2.imdecode(edge_image_array, cv2.IMREAD_GRAYSCALE)

    # 'resize_factor': gcode_size / image_size,
    # 'start_point': np.array([0, 0])

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
    Output("mill_gcode_button", "n_clicks"),
    State("gcode_store", "data"),
    Input("mill_gcode_button", "n_clicks")
)
def mill_gcode(gcode, n_clicks):
    if n_clicks is not None and n_clicks > 0:
        app = Application()    # Kickstart the main application
        app.activate_gui(com_port=app.port_list)
        app.controller_send_cmd('G0 X-250 Y-400')
        app.set_nullpunkt_XY()
        app.controller_send_cmd('G0 Z-130')
        app.set_nullpunkt_Z()
        
        # app.start_file_execution(gcode.split('\n'))        
        # time.sleep(1)
        app.controller_send_cmd('$H')
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

    for contour in ordered_contours:
        contour = np.array(contour)
        x_approx = contour[:, :, 0].flatten()
        y_approx = contour[:, :, 1].flatten()

        plt.plot(x_approx, y_approx, color='blue')

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
