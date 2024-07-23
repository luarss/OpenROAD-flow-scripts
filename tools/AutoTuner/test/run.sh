#!/bin/bash

# docker compose -f docker-compose-ray27.yaml build --no-cache
# docker compose -f docker-compose-ray27.yaml up -d

# sleep 18000 # 5 hours
# docker compose -f docker-compose-ray27.yaml down

# docker compose -f docker-compose-ray28.yaml build --no-cache
# docker compose -f docker-compose-ray28.yaml up -d

# sleep 18000 # 5 hours
# docker compose -f docker-compose-ray28.yaml down
# docker compose -f docker-compose-ray29.yaml build --no-cache
# docker compose -f docker-compose-ray29.yaml up -d
# docker compose -f docker-compose-ray29.yaml down

DESIGN_LIST=("gcd" "aes" "ibex")
PLATFORM_LIST=("asap7" "sky130hd" "ihp-sg13g2")

for DESIGN in "${DESIGN_LIST[@]}"; do
    for PLATFORM in "${PLATFORM_LIST[@]}"; do
        sed "s|{{DESIGN}}|${DESIGN}|g" .env.example > .env.tmp
        sed "s|{{PLATFORM}}|${PLATFORM}|g" .env.tmp > .env
        docker compose -f ray27-split.yaml build --no-cache
        docker compose -f ray27-split.yaml up
        # sleep 5000
        docker compose -f ray27-split.yaml down
        docker compose -f ray27-split.yaml log > ${DESIGN}_${PLATFORM}_ray27.log

        # delete docker cache
        docker system prune -a -f
    done
done