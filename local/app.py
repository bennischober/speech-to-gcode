import dash
from dash import html, dcc, Input
import dash_bootstrap_components as dbc
from components.speech_to_text_component import get_speech_to_text_component
# from components.speech_to_text.callbacks import get_callbacks as get_speech_to_text_callbacks
from components.stable_diffusion import get_stable_diffusion_component
from components.image_preprocessing import get_image_preprocessing_component
from components.image_to_gcode import get_image_to_gcode_component

# Load Icons
html.I(className='fas fa-microphone')

external_stylesheets = [
    dbc.themes.DARKLY,
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

# Definieren Sie die Farben für den Farbverlauf
colors = {
    'background': '#1a2a6c',
    'background2': '#b21f1f',
    'text': '#ffffff'
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
                get_speech_to_text_component(),
                get_stable_diffusion_component(),
                get_image_preprocessing_component(),
                get_image_to_gcode_component(),
            ],
            style={
                'background-image': f'linear-gradient(to bottom right, {colors["background"]}, {colors["background2"]})',
                'padding': '50px',
                'border-radius': '10px',
                'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
            }
        )
    ],
    style={
        'background-color': colors['background']
    }
)

# set callbacks for speech_to_text component
# get_speech_to_text_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True) # Maximale Länge der URL auf 1 MB setzen
