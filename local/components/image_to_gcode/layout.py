from dash import html, dcc
import dash_bootstrap_components as dbc

# This layout vaiable contains the whole layout of the GCODE component

layout = dbc.Card(
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
                                                                step=2,
                                                                value=5, 
                                                                min=1,
                                                                max=25,
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
                            dbc.Button("GCODE neu laden", id="reload_gcode", color="primary", className="mr-2", 
                                       style={'width': '100%', 'height': '50px', 'margin': '15px 0 20px 0', 'font-size': '20px'})
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
                        html.Div([
                                dbc.Button("GCODE Kopieren", id="copy_gcode_button", className='gcode_controll_buttons', color="primary")
                            ]
                        ),
                        html.Div([
                                dbc.Button("GCODE Fräsen", id="mill_gcode_button", className='gcode_controll_buttons', color="primary")
                            ]
                        ),
                    ], 
                    style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),
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