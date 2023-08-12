#!/bin/bash
docker system prune -f

docker image build -f dockerfile -t image_server:1.0 .

docker-compose down
docker-compose up -d
