from dash import html, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import numpy as np
import cv2
from components.image_preprocessing import get_dilated_img, get_org_img

path = "components\image_to_gcode\gcode.tap"
gcode_data = "Kein Code geladen ..."


############## Image to GCode ###############

class MyImageProcessing:
    def __init__(self) -> None:

        self.resize_scale = 100
        self.image = None

        self.image_width = None
        self.image_heigth = None
        self.image_resize = None

        self.image_threshold = None
        self.image_white_contour = None

        self.contour_minArcLength = 0

        self.final_contours = None

    def resize_image(self, image):
        self.image_heigth, self.image_width, _ = np.shape(image)
        newWidth = int(self.image_width * self.resize_scale / 100)
        newHeight = int(self.image_heigth * self.resize_scale / 100)
        newDimension = (newWidth, newHeight)
        # resize image
        self.image_resize = cv2.resize(
            image, newDimension, interpolation=cv2.INTER_AREA)
        self.image_resize_heigth, self.image_resize_width, _ = np.shape(
            self.image_resize)
        # self.image_blank = np.ones((self.image_resize_heigth,self.image_resize_width, 3), np.uint8)*255
        return self.image_resize

    def contour(self, image_threshold):
        self.image_white_contour = np.ones(
            (self.image_resize_heigth, self.image_resize_width, 3), np.uint8)*255
        contours, hierarchy = cv2.findContours(
            image_threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        self.final_contours = []
        for i, c in enumerate(contours):
            areaContour = cv2.arcLength(c, True)
            area_min = self.contour_minArcLength
            area_max = 1000000000
            if areaContour < area_min or area_max < areaContour:
                continue
            else:
                self.final_contours.append(c)


class MyGcode:
    def __init__(self) -> None:
        self.z_safe_hight = 10.0
        self.z_working_hight = 0.5
        self.z_depth = 1
        self.z_feed = 500
        self.xy_feed = 1000
        self.spindle_speed = 24000

        self.save_file_str = None
        self.gcode_data = []

    def generate_gcode(self, contours):
        # set contour to (0|0)
        minX = 1000
        maxX = 0
        minY = 1000
        maxY = 0

        for count, c in enumerate(contours):
            tmp_minX = np.min(c[:, :, 0])
            tmp_minY = np.min(c[:, :, 1])
            tmp_maxX = np.max(c[:, :, 0])
            tmp_maxY = np.max(c[:, :, 1])
            if tmp_minX < minX:
                minX = tmp_minX
            if tmp_minY < minY:
                minY = tmp_minY
            if tmp_maxX > maxX:
                maxX = tmp_maxX
            if tmp_maxY > maxY:
                maxY = tmp_maxY

        contours_list = []
        for count, contour in enumerate(contours):
            contour_list = []
            for points in contour:
                contour_list.append([points[0][0] - minX, points[0][1] - minY])

            contours_list.append(contour_list)

        # write g-code
        gcode_start = [f"M03 S{self.spindle_speed}",
                       f"G00 Z{self.z_safe_hight}"]
        gcode_end = [f"G00 Z{self.z_safe_hight}", "G00 X0 Y0", "M05", "M30"]

        self.gcode_data = []

        for count, elem in enumerate(gcode_start):
            self.gcode_data.append(f"{elem}\n")

        for count_contour, contour in enumerate(contours_list):

            tmp_contour_len = len(contour)
            self.gcode_data.append(
                f"{tmp_contour_len}#####################################\n")

            self.gcode_data.append(f"G00 X{contour[0][0]} Y{contour[0][1]}\n")
            self.gcode_data.append(f"G00 Z0\n")
            self.gcode_data.append(f"G01 Z-{self.z_depth} F{self.z_feed}\n")

            if tmp_contour_len == 2:
                self.gcode_data.append(
                    f"G01 X{contour[1][0]} Y{contour[1][1]} F{self.xy_feed}\n")

            self.gcode_data.append(f"G00 Z{self.z_working_hight}\n")

            if tmp_contour_len > 2:
                for i in range(tmp_contour_len-1):
                    if i == 0:
                        self.gcode_data.append(
                            f"G01 X{contour[i+1][0]} Y{contour[i+1][1]} F{self.xy_feed}\n")
                    else:
                        self.gcode_data.append(
                            f"G01 X{contour[i+1][0]} Y{contour[i+1][1]}\n")
                self.gcode_data.append(f"G00 Z{self.z_working_hight}\n")

        for count, elem in enumerate(gcode_end):
            self.gcode_data.append(f"{elem}\n")

        # Save the G-code to a file
        with open(self.save_file_str, "w") as f:
            f.writelines(self.gcode_data)


def image_to_gcode(dilated, original):

    # Resize img
    imgpro = MyImageProcessing()
    imgpro.resize_scale = 200
    img = imgpro.resize_image(original)

    # Konturen speichern
    imgpro.contour(dilated)

    # GCode erstellen
    gcode = MyGcode()
    gcode.save_file_str = path
    gcode.generate_gcode(imgpro.final_contours)

    global gcode_data
    gcode_data = gcode.gcode_data


code_style = {
    "color": "black",
    "white-space": "pre-wrap",
    "word-wrap": "break-word",
    'text-align': 'left',
    'color': '#000000',
    'margin-left': '10px'
}

### Button Callbacks ###

# Define the callback function to toggle the first collapse


@callback(
    Output("code_collapse", "is_open"),
    [Input("code_button", "n_clicks")],
    [State("code_collapse", "is_open")],
)
def toggle_collapse1(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

# Define the callback function to open the second collapse once


@callback(
    Output("gcode_collapse", "is_open"),
    [Input("gcode_button", "n_clicks")],
    [State("gcode_collapse", "is_open")],
)
def open_collapse2(n_clicks, is_open):
    if n_clicks and not is_open:
        return True
    return is_open

### update gcode ###


@callback(
    Output('code-list', 'children'),
    Input('gcode_button', 'n_clicks')
)
def update_code_list(n_clicks):

    dilated = get_dilated_img()
    org = get_org_img()
    gcode_tmp = "Kein Code geladen ..."
    if dilated is not None and org is not None:
        image_to_gcode(dilated, org)
        gcode_tmp = "\n".join(gcode_data)
    return gcode_tmp

### ### ###


def get_image_to_gcode_component():
    return dbc.Card(
        children=[
            dbc.CardHeader('Image to GCode'),
            html.Div(id='test'),

            dbc.CardBody([

                dbc.Button("Generate GCode", color="primary",
                           className="me-1", id="gcode_button"),


                dbc.Collapse([
                    html.Div("GCode erfolgreich erstellt!",
                             style={'font-size': '15px'}),
                    html.Div(
                        html.I(
                            className='bi bi-check-lg',
                            style={
                                'font-size': '30px',
                            }),
                        id='icon',
                        style={
                            "border-radius": "50%",
                            "background-color": "green",
                            "width": "50px",
                            "height": "50px",
                            'margin': 'auto',
                            'display': 'flex',
                            'justify-content': 'center',
                            'align-items': 'center'
                        }),
                    dbc.Button("Hier Klicken, um den Code anzuzeigen", id="code_button", className="mt-3", style={
                               'width': '60vw', 'margin': 'auto', 'margin-bottom': '20px', 'color': '#ffffff'}),
                    dbc.Collapse([
                        html.H6("G-Code:"),
                        dbc.CardBody([
                            html.Pre(
                                id='code-list', children='\n'.join(gcode_data), style=code_style)
                        ]),
                    ], style={'background': '#ffffff', 'margin': 'auto', 'width': '60vw'}, id="code_collapse", is_open=False),
                    html.Div("Bereit zum Fräßen!"),
                    html.Div(
                        "Klicken Sie auf     -Erneute Aufnahme-     um ein weiteres Bild zu generieren!"),
                ], id="gcode_collapse", is_open=False),

            ]),
        ],
        className='mb-4',
        style={
            'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
            'text-align': 'center',
            'margin': ' 25px auto',
        })
