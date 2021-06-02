#!/bin/bash
set -e

# Needs gitlab and aws credentials

# docker network create chart
# exported because we're running locally
export DATABASE=billboard_charts
export DB_TYPE=mysql
export DB_USERNAME=chart
export DB_HOST=localhost:3306
export PASS=$(openssl rand -base64 12)
export PIPENV_DONT_LOAD_ENV=1

DB_CONTAINER_AUTO_TAG=registry.gitlab.com/joyfulflyer/billboard-db:auto
DB_CONTAINER_TIERS_TAG=registry.gitlab.com/joyfulflyer/billboard-db:tiers
DB_CONTAINER_LATEST_TAG=registry.gitlab.com/joyfulflyer/billboard-db:latest
SONG_CONVERTER_TAG=registry.gitlab.com/joyfulflyer/billboard-song-converter:latest

TEMP_DIRECTORY=temp

FILE_NAME=songs$(date +"%Y%m%d")-tier.sql
DB_CONTAINER_NAME=tierdb
NETWORK_NAME=songnetwork

docker network create $NETWORK_NAME

docker pull $DB_CONTAINER_AUTO_TAG
docker pull $SONG_CONVERTER_TAG

docker run -d \
    -e MYSQL_DATABASE=$DATABASE \
    -e MYSQL_USER=$DB_USERNAME \
    -e MYSQL_PASSWORD=$PASS \
    -e MYSQL_RANDOM_ROOT_PASSWORD=true \
    --name $DB_CONTAINER_NAME \
    --network $NETWORK_NAME \
    --rm \
    $DB_CONTAINER_AUTO_TAG

sleep 1m

# pipenv run python start.py -t -w 180
docker run \
    -e DATABASE=$DATABASE \
    -e DB_TYPE=mysql \
    -e DB_USERNAME=$DB_USERNAME \
    -e DB_HOST=$DB_CONTAINER_NAME:3306 \
    -e PASS=$PASS \
    --network $NETWORK_NAME \
    --rm \
    $SONG_CONVERTER_TAG \
    python start.py -t -w 180

mkdir $TEMP_DIRECTORY
cd $TEMP_DIRECTORY

docker exec -i $DB_CONTAINER_NAME mysqldump -u $DB_USERNAME --password=$PASS $DATABASE >$FILE_NAME

# docker cleanup
(
    docker stop $DB_CONTAINER_NAME
    docker network rm $NETWORK_NAME
)

# build docker container

# create temp docker file
(
    printf "FROM mysql:8.0.22\n\nCOPY $FILE_NAME /docker-entrypoint-initdb.d/" >tempdockerfile
    docker build --pull --rm -f "./tempdockerfile" --tag $DB_CONTAINER_TIERS_TAG .
    docker tag $DB_CONTAINER_TIERS_TAG $DB_CONTAINER_AUTO_TAG
    docker push $DB_CONTAINER_TIERS_TAG
    docker push $DB_CONTAINER_AUTO_TAG
)

# upload gzipped backup to s3
(
    gzip -k $FILE_NAME
    aws s3 cp $FILE_NAME.gz s3://billboard-viewer-db
    rm $FILE_NAME.gz
)

wait

#cleanup
cd ..
rm -r $TEMP_DIRECTORY
