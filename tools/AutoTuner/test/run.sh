#!/bin/bash

TIMEOUT=18000 # 5h
DESIGN_LIST=("gcd" "aes" "ibex")
PLATFORM_LIST=("asap7" "sky130hd" "ihp-sg13g2")
RAY_LIST=("27" "28" "29")

# Determine number of cores (Values are chosen based on 64core, 512Gb machine, adjust accordingly)
JOBS_ASAP7_AES=30 # peak: 16Gb
JOBS_ASAP7_IBEX=38 # peak: 13Gb
JOBS_DEFAULT=64

for RAY in "${RAY_LIST[@]}"; do
    for DESIGN in "${DESIGN_LIST[@]}"; do
        for PLATFORM in "${PLATFORM_LIST[@]}"; do
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
            docker compose -f ray${RAY}-split.yaml build --no-cache
            docker compose -f ray${RAY}-split.yaml up -d
            sleep $TIMEOUT
            docker compose -f ray${RAY}-split.yaml down

            # TODO fix log saving for docker compose up: https://stackoverflow.com/questions/69613129/how-to-save-the-logs-for-docker-compose-up-d-build
            docker compose -f ray${RAY}-split.yaml logs > ${DESIGN}_${PLATFORM}_ray${RAY}.log

            # delete docker cache
            docker builder prune -f
        done
    done
done