#!/bin/bash

DESIGN_LIST=("gcd" "aes" "ibex")
PLATFORM_LIST=("asap7" "sky130hd" "ihp-sg13g2")
RAY_LIST=("27" "28" "29")

for RAY in "${RAY_LIST[@]}"; do
    for DESIGN in "${DESIGN_LIST[@]}"; do
        for PLATFORM in "${PLATFORM_LIST[@]}"; do
            sed "s|{{DESIGN}}|${DESIGN}|g" .env.example > .env.tmp
            sed "s|{{PLATFORM}}|${PLATFORM}|g" .env.tmp > .env
            docker compose -f ray${RAY}-split.yaml build --no-cache
            docker compose -f ray${RAY}-split.yaml up
            docker compose -f ray${RAY}-split.yaml down
            docker compose -f ray${RAY}-split.yaml logs > ${DESIGN}_${PLATFORM}_ray${RAY}.log

            # delete docker cache
            docker builder prune -f
        done
    done
done