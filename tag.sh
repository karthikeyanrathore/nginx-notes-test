#!/bin/bash

set -ex

VERSION=$1 # should be float/int value
if [ -z $VERSION ]; then
    echo "error, need version arg"
    exit 1
fi

if ! [[ $VERSION =~ [^a-zA-Z] ]]; then
    echo "Invalid version arg"
    exit 1
fi

IMAGE_COMPOSE_FILE="docker-compose-image.yml"
COMPOSE_FILE="docker-compose-offline.yml"
COMPOSE_CMD="docker compose"

IMAGE_API="nginx-notes-test-notes-api"

build_up_services(){
    $COMPOSE_CMD down -v --remove-orphans; \
    $COMPOSE_CMD -f $COMPOSE_FILE down -v --remove-orphans;
    sleep 2

    # unset $VERSION;
    export VERSION=$VERSION;
    $COMPOSE_CMD -f $COMPOSE_FILE pull; \
    $COMPOSE_CMD -f $COMPOSE_FILE build; 
    sleep 4
}

spin_up_services(){
    docker tag $IMAGE_API pc.registry/notes-api:$VERSION
    # might have to pull nginx, postgres images if not present locally.
    # $COMPOSE_CMD -f $IMAGE_COMPOSE_FILE build; \
    # $COMPOSE_CMD -f $IMAGE_COMPOSE_FILE up
}


build_up_services
spin_up_services

# example usage: ./tag.sh 1.0
# clean up
# docker-compose down -v --remove-orphans;
# docker-compose -f docker-compose-image.yml  down -v --remove-orphans;