FROM python:3.9-slim-buster

WORKDIR /usr/app/src

RUN pip3 install --upgrade diffusers[torch] && \
    pip3 install transformers && \
    pip3 install Flask && \
    pip3 install Pillow && \
    pip3 install numpy && \
    pip3 install open_clip_torch && \
    pip3 install librosa soundfile

COPY rest_api_0_4.py ./

# copy other files from pipeline folder
COPY pipeline/ ./pipeline/

CMD [ "python", "./rest_api_0_4.py"]