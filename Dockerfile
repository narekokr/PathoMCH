FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}"
ENV CUDA_DIR="/usr/local/cuda"
RUN apt-get update && \
  apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3.11-distutils \
    wget \
    curl \
    git \
    build-essential \
    libfreetype6-dev \
    libhdf5-dev \
    libpng-dev \
    pkg-config \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3.11 get-pip.py && \
    rm get-pip.py

RUN python3 --version && pip3 --version

WORKDIR /workspace

COPY . /workspace
RUN pip3 install -r requirements.txt

WORKDIR /workspace/src
CMD ["python3.11", "model.py"]
