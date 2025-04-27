#!/bin/bash


## Usage
## sudo ./compose.sh 'up' # To start the services
## sudo ./compose.sh 'down' # To remove the services
## sudo ./compose.sh 'down --volumes' # To remove the services volumes
## sudo ./compose.sh 'build' # To build the images
## sudo ./compose.sh 'build --no-cache' to build without cache

(
source .env

command="docker compose"
if [ "$($command version | grep 'version v2')" = "" ]; then
    command=docker-compose
fi

if [ "$DEPLOYMENT_TYPE" == 'postgres' ]; then
    $command -f docker-compose-postgres.yml $1
elif [ "$DEPLOYMENT_TYPE" == 'postgres-ssl' ]; then
    $command -f docker-compose-postgres-ssl.yml $1
elif [ "$DEPLOYMENT_TYPE" == 'sqlite' ]; then
    $command -f docker-compose-sqlite.yaml $1
elif [ "$DEPLOYMENT_TYPE" == 'sqlite-ssl' ]; then
    $command -f docker-compose-sqlite-ssl.yaml $1
else
  echo "Please set DEPLOYMENT_TYPE env variable to on of 'postgres', 'postgres-ssl', 'sqlite', 'sqlite-ssl'"
fi
)

