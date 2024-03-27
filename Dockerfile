# Base image -> https://github.com/runpod/containers/blob/main/official-templates/base/Dockerfile
# DockerHub -> https://hub.docker.com/r/runpod/base/tags
FROM runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04

WORKDIR /
# The base image comes with many system dependencies pre-installed to help you get started quickly.
# Please refer to the base image's Dockerfile for more information before adding additional dependencies.
# IMPORTANT: The base image overrides the default huggingface cache location.


# --- Optional: System dependencies ---
# COPY builder/setup.sh /setup.sh
# RUN /bin/bash /setup.sh && \
#     rm /setup.sh

# env setup
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y curl git ca-certificates && \
    git clone https://github.com/m000lie/tts-mooolie.git && \
    apt-get install -y libsndfile1-dev && \
    cd tts-mooolie && pip install --ignore-installed --no-cache-dir --timeout 1000 .[all,dev,notebooks] && \
    pip install git+https://github.com/m000lie/Trainer.git --timeout 1000 && \
    apt install nvidia-cudnn -y && pip install gradio faster_whisper

RUN pip install --force-reinstall soundfile

# Python dependencies
COPY builder/requirements.txt requirements.txt
COPY builder/requirements.dev.txt requirements.dev.txt
RUN pip install -r requirements.txt --no-cache-dir --timeout 1000&& pip install -r requirements.dev.txt --no-cache-dir --timeout 1000 && \ 
    rm requirements.txt && rm requirements.dev.txt

# NOTE: The base image comes with multiple Python versions pre-installed.
#       It is reccommended to specify the version of Python when running your code.



# Add src files (Worker Template)
COPY handler.py /
COPY inference.py /

ADD voices /voices

CMD ["python", "handler.py"]
