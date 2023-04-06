from dash import html
import dash_bootstrap_components as dbc

def get_stable_diffusion_component():
    return dbc.Card(
                    children=[
                        dbc.CardHeader('Stable Diffusion'),
                        dbc.CardBody('Short Description'),
                        # Hier fügen Sie Ihre zweite Komponente hinzu
                    ],
                    className='mb-4',
                    style={
                        'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
                    }
                )