import os
from waitress import serve
from src.app import app

port = os.getenv('API_PORT', 5000)

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=port)

# Docker Commands: (OLD)
# docker image build -t stbescho_apis:0.6 /home/stbescho/text_to_gcode/
# docker run -d --gpus '"device=1"' -p 5000:5000 -v /home/stbescho/models:/models --name stbescho_apis stbescho_apis:0.6


# DOCKER COMPOSE COMMANDS:

# before running docker compuse up, goto /api/ and execute: chmod +x entrypoint.sh

# builds the image and runs the container in detached mode, remove --build if you don't want to rebuild the image
# docker compose up --build -d

# stops the container and removes it
# docker compose down
