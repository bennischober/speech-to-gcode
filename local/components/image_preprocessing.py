from dash import html
import dash_bootstrap_components as dbc

def get_image_preprocessing_component():
    return dbc.Card(
                    children=[
                        dbc.CardHeader('Image Preprocessing'),
                        dbc.CardBody('Short Description'),
                        # Hier fügen Sie Ihre dritte Komponente hinzu
                    ],
                    className='mb-4',
                    style={
                        'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
                    }
                )