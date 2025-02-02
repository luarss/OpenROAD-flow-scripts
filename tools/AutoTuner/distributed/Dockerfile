ARG BASE_TAG
FROM openroad/flow-ubuntu22.04-builder:${BASE_TAG:-latest}

# Install rsync (https://github.com/ray-project/ray/issues/40566)
# ssh: to communicate with other nodes within image.
# sudo: for grpc calls in ray.
RUN apt-get update && \
    apt-get install -y rsync openssh-client sudo && \
    rm -rf /var/lib/apt/lists/*a

# Install AT required packages
RUN rm -rf ~/.cache/pip
RUN pip3 install --upgrade pip
RUN pip3 cache purge
RUN cd /OpenROAD-flow-scripts/tools/AutoTuner && \
    pip3 install --no-cache-dir -e .

# ORFS installation dir
WORKDIR /OpenROAD-flow-scripts/tools/AutoTuner
