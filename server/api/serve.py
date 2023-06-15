import os
from waitress import serve
from src.app import app

port = os.getenv('API_PORT', 5000)

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=port)

# Docker Commands:
# docker image build -t stbescho_apis:0.6 /home/stbescho/text_to_gcode/
# docker run -d --gpus '"device=1"' -p 5000:5000 -v /home/stbescho/models:/models --name stbescho_apis stbescho_apis:0.6
