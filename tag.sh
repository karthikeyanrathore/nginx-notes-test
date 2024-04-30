#!/bin/bash

set -ex

VERSION=$1
if [ -z $VERSION ]; then
    echo "error, need version arg"
    exit 1
fi


COMPOSE_FILE="docker-compose-offline.yml"
COMPOSE_CMD="docker compose"


IMAGE_INGRESS="nginx:1.25.3-alpine"
IMAGE_API="nginx-notes-test-notes-api"
IMAGE_DB="postgres:12.3-alpine"

spin_up_services(){
    $COMPOSE_CMD down -v --remove-orphans; \
    $COMPOSE_CMD -f $COMPOSE_FILE down -v --remove-orphans;
    sleep 2

    reset; export API_VERSION=$VERSION
    $COMPOSE_CMD -f $COMPOSE_FILE pull; \
    $COMPOSE_CMD -f $COMPOSE_FILE build; 
    sleep 4
}

tag_images(){
    docker tag $IMAGE_INGRESS offline.registry/nginx-performer:$VERSION && \
    echo offline.registry/nginx-performer:$VERSION
    
    docker tag $IMAGE_API offline.registry/notes-api:$VERSION && \
    echo offline.registry/notes-api:$VERSION
    
    docker tag $IMAGE_DB offline.registry/notes-db$VERSION && \
    echo offline.registry/notes-db$VERSION
}


spin_up_services
tag_images

# ./tag.sh 1.0