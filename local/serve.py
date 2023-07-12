import os
from waitress import serve
from app import app

if __name__ == '__main__':
    env = os.environ.get('ENV', 'dev')

    if env == 'dev':
        app.run(debug=True)
    elif env == 'prod':
        serve(app.server, host='0.0.0.0', port=8050)
    else:
        raise ValueError(f'Unknown environment: {env}')
