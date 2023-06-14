FROM python:3.9-slim-buster

WORKDIR /usr/app/src

# Set the transformers cache location
ENV TRANSFORMERS_CACHE=/models

RUN pip3 install --upgrade diffusers[torch] && \
    pip3 install transformers && \
    pip3 install Flask && \
    pip3 install Pillow && \
    pip3 install open_clip_torch && \
    pip3 install librosa soundfile

COPY apis_0_6.py ./

COPY pipelines/ ./pipelines/
COPY lib/ ./lib/

CMD [ "python", "./apis_0_6.py"]

# Declare models as a volume
VOLUME /models
