FROM python:3.9-slim-buster

WORKDIR /usr/app/src

RUN pip3 install --upgrade diffusers[torch] && \
    pip3 install transformers && \
    pip3 install Flask && \
    pip3 install Pillow && \
    pip3 install transformers
    # pip3 install torch

COPY stable_diffusion_rest_api_0_2.py ./

CMD [ "python", "./stable_diffusion_rest_api_0_2.py"]