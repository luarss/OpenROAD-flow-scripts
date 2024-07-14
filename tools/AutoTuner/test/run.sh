#!/bin/bash

docker compose -f docker-compose-ray27.yaml build --no-cache
docker compose -f docker-compose-ray27.yaml up -d

# sleep 18000 # 5 hours
# docker compose -f docker-compose-ray27.yaml down

# docker compose -f docker-compose-ray28.yaml build --no-cache
# docker compose -f docker-compose-ray28.yaml up -d

# sleep 18000 # 5 hours

# docker compose -f docker-compose-ray29.yaml build --no-cache
# docker compose -f docker-compose-ray29.yaml up -d
