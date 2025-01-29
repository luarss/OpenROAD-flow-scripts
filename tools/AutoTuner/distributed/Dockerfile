ARG BASE_TAG
FROM openroad/flow-ubuntu22.04-builder:${BASE_TAG:-latest}

# Install rsync (https://github.com/ray-project/ray/issues/40566)
# Install ssh to communicate with other nodes within image.
RUN apt-get update && \
    apt-get install -y rsync openssh-client && \
    rm -rf /var/lib/apt/lists/*a

# Install AT required packages
RUN rm -rf ~/.cache/pip
RUN pip3 cache purge
RUN pip3 install --no-cache-dir -r /OpenROAD-flow-scripts/tools/AutoTuner/requirements.txt

# ORFS installation dir
WORKDIR /OpenROAD-flow-scripts/tools/AutoTuner/src/autotuner
