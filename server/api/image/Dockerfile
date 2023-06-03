FROM python:3.9-slim-buster

WORKDIR /usr/app/src

RUN pip3 install --upgrade diffusers[torch] && \
    pip3 install transformers && \
    pip3 install Flask && \
    pip3 install Pillow && \
    pip3 install open_clip_torch

COPY image_api_0_5.py ./

COPY pipeline/ ./pipeline/

CMD [ "python", "./image_api_0_5.py"]
