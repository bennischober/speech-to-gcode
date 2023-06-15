FROM python:3.9-slim-buster

WORKDIR /usr/app/src

# Set the transformers cache location
ENV TRANSFORMERS_CACHE=/models
ENV API_PORT=5000

RUN pip3 install --upgrade diffusers[torch] && \
    pip3 install transformers && \
    pip3 install Flask && \
    pip3 install Pillow && \
    pip3 install open_clip_torch && \
    pip3 install librosa soundfile && \
    pip3 install waitress && \
    pip3 install -U flask-cors

COPY serve.py ./

COPY pipelines/ ./pipelines/
COPY lib/ ./lib/
COPY src/ ./src/

CMD [ "python", "./serve.py"]

# Declare models as a volume
VOLUME /models
