import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.speech_to_text.main_component import get_speech_to_text_component
from components.stable_diffusion.main_component import get_stable_diffusion_component, get_selected_preload_image
from components.image_preprocessing.main_component import get_image_preprocessing_component
from components.image_to_gcode.main_component import get_image_to_gcode_component
from components.controlling.main_component import FuturisticButtons
import matplotlib
from utils.config import DEFAUL_GCODE_STATS, DYNAMIC_PARAMS

# Load Icons
html.I(className='fas fa-microphone')

external_stylesheets = [
    dbc.themes.DARKLY,
    dbc.icons.BOOTSTRAP,
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
    'style.css'
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)


# Definieren Sie die Farben für den Farbverlauf
colors = {
    'background': '#1a2a6c',
    'background2': '#b21f1f',
    'text': '#ffffff',
    'blue': '#000080',
    'red': '#8B0000',
}

# Layout der App
app.layout = html.Div(
    children=[
        # Navigation
        dbc.NavbarSimple(
            brand='Master Projekt',
            color='primary',
            dark=True,
            className='mb-5'
        ),

        # Beschreibung der App
        html.Div(
            children=[
                html.H1(
                    children='Speech To GCode',
                    style={
                        'textAlign': 'center',
                        'color': colors['text']
                    }
                ),
                html.P(
                    children='Ein Programm zur Generierung von C&C Fräsen lebaren Code durch Sprache.',
                    style={
                        'textAlign': 'center',
                        'color': colors['text']
                    }
                )
            ],
            className='mb-5'
        ),

        # Komponenten
        html.Div(
            children=[
                # The Stores
                dcc.Store(id='base64_selected_stable_diff_img_store', data=get_selected_preload_image()),
                dcc.Store(id='base64_edge_image_store'),
                dcc.Store(id='gcode_store'),
                dcc.Store(id='ordered_contours_store'),
                dcc.Store(id='gcode_stats_store', data=DEFAUL_GCODE_STATS),
                dcc.Store(id='dynamic_params', data=DYNAMIC_PARAMS),
                dcc.Store(id='recent_gcode_generated_successfully_store', data=None),

                # The Components
                get_speech_to_text_component(),
                get_stable_diffusion_component(),
                get_image_preprocessing_component(),
                get_image_to_gcode_component(),
                FuturisticButtons(),
            ],
            style={
                'backgroundImage': f'linear-gradient(to bottom right, {colors["blue"]}, {colors["red"]})',
                'padding': '50px',
                'borderRadius': '10px',
                'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
            }
        )
    ],
    style={
        'backgroundColor': colors['background']
    }
)

if __name__ == '__main__':
    # is needed for gcode image
    matplotlib.use('Agg')
