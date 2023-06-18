# Using PyTorch image as the base
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-devel

WORKDIR /usr/app/src

# Set the transformers cache location
ENV TRANSFORMERS_CACHE /models
# Set the NLTK_DATA location
ENV NLTK_DATA /models/nltk_data
ENV LOGS_DIR /logs
ENV API_PORT 5000
ENV BUILD_WITH_CUDA True
ENV CUDA_HOME /usr/local/cuda-11.7/

ENV IMAGE_DIR = /images

# Update the repository sources list and install dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3.9-dev \
    git \
    gcc g++ \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    libgl1-mesa-glx \
    libsndfile1

# Install necessary python packages
RUN pip install --upgrade diffusers \
    transformers \
    nltk \
    Flask \
    Pillow \
    open_clip_torch \
    librosa soundfile \
    waitress \
    -U flask-cors \
    cython pycocotools ninja \
    accelerate sacremoses

# Install dependencies for building custom C++ ops
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libboost-python-dev \
    ninja-build

# Build custom C++ ops and install GroundingDINO from source
RUN git clone https://github.com/IDEA-Research/GroundingDINO.git

WORKDIR /usr/app/src/GroundingDINO
RUN pip install -e .

WORKDIR /usr/app/src

COPY serve.py ./
COPY pipelines/ ./pipelines/
COPY lib/ ./lib/
COPY src/ ./src/

COPY entrypoint.sh /usr/app/src/entrypoint.sh

CMD ["/usr/app/src/entrypoint.sh"]


VOLUME /models
VOLUME /logs
VOLUME /images
