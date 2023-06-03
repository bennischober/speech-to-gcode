FROM python:3.9-slim-buster

WORKDIR /usr/app/src

RUN pip3 install transformers[torch] && \
    pip3 install Flask && \
    pip3 install librosa soundfile

COPY text_api_0_5.py ./

COPY pipeline/ ./pipeline/

CMD [ "python", "./text_api_0_5.py"]
