FROM python:3.9-slim-buster

WORKDIR /usr/app/src

RUN pip3 install --upgrade diffusers[torch] && \
    pip3 install transformers && \
    pip3 install Flask && \
    pip3 install Pillow && \
    pip3 install numpy

COPY rest_api_0_3.py ./

CMD [ "python", "./rest_api_0_3.py"]