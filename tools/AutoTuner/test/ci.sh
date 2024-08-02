#!/bin/bash

# This script is used to generate 10 different runs.

DESIGN_LIST=("gcd" "aes" "ibex")
PLATFORM_LIST=("asap7" "sky130hd" "ihp-sg13g2")
NUM_TRIALS=10
JOBS_ASAP7_AES=2 # peak: 16Gb
JOBS_ASAP7_IBEX=3 # peak: 13Gb
JOBS_DEFAULT=6

for DESIGN in "${DESIGN_LIST[@]}"; do
   for PLATFORM in "${PLATFORM_LIST[@]}"; do
        for i in $(seq 1 $NUM_TRIALS); do
            if [ "$DESIGN" == "aes" ] && [ "$PLATFORM" == "asap7" ]; then
                JOBS=$JOBS_ASAP7_AES
            elif [ "$DESIGN" == "ibex" ] && [ "$PLATFORM" == "asap7" ]; then
                JOBS=$JOBS_ASAP7_IBEX
            else
                JOBS=$JOBS_DEFAULT
            fi

            cp .env.example .env
            sed -i "s|{{DESIGN}}|${DESIGN}|g" .env
            sed -i "s|{{PLATFORM}}|${PLATFORM}|g" .env
            sed -i "s|{{JOBS}}|${JOBS}|g" .env 

            filename=${DESIGN}_${PLATFORM}_run${i}.log
            touch $filename
            docker compose -f ray${RAY}-split.yaml build --no-cache
            docker compose -f ray${RAY}-split.yaml up -d

            # Get the container ID and append it to the log file
            container_id=$(docker compose -f ray${RAY}-split.yaml ps -q)
            echo "Container ID: $container_id" >> $filename
            docker inspect --format='{{.LogPath}}' $container_id >> $filename

            sleep $TIMEOUT
            docker compose -f ray${RAY}-split.yaml down

            # delete docker cache
            docker builder prune -f
        done
        # wait till all docker containers are down also, how to we make this parallel?

    done
done