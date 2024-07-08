# Base image 
FROM openroad/flow-ubuntu22.04-builder:latest

# Set and assert that this arg is set
ARG REQUIREMENTS_FILE
RUN if [ -z "$REQUIREMENTS_FILE" ]; then echo "REQUIREMENTS_FILE is not set"; exit 1; fi

# Install pip packages
COPY $REQUIREMENTS_FILE /OpenROAD-flow-scripts/tools/AutoTuner/$REQUIREMENTS_FILE
RUN python3 -m pip install -r /OpenROAD-flow-scripts/tools/AutoTuner/$REQUIREMENTS_FILE

# Print ray version
RUN python3 -c "import ray; print(ray.__version__)"

# Run the necessary commands and export the result
WORKDIR /OpenROAD-flow-scripts/tools/AutoTuner/src/autotuner
CMD ["python3", "distributed.py", "--design", "gcd", "--platform", "asap7", "--config", "../../../../flow/designs/asap7/gcd/autotuner.json", "tune", "--samples", "50"]