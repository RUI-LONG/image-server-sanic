#!/bin/bash
sudo docker system prune -f

sudo docker image build -f dockerfile -t image_server:1.0 .

sudo docker-compose down
sudo docker-compose up -d
