#!/bin/bash
set -e

# Needs gitlab and aws credentials

# docker network create chart
# exported because we're running locally
export DATABASE=billboard_charts
export DB_TYPE=mysql
export DB_USERNAME=chart
export DB_HOST=localhost:3306
export PASS=temporaryaccess
export PIPENV_DONT_LOAD_ENV=1

DB_CONTAINER_AUTO_TAG=registry.gitlab.com/joyfulflyer/billboard-db:auto
DB_CONTAINER_TIERS_TAG=registry.gitlab.com/joyfulflyer/billboard-db:tiers
TEMP_DIRECTORY=temp

FILE_NAME=songs$(date +"%Y%m%d")-tier.sql
DB_CONTAINER_NAME=tierdb

docker pull $DB_CONTAINER_AUTO_TAG

docker run -d \
    -e MYSQL_DATABASE=$DATABASE \
    -e MYSQL_USER=$DB_USERNAME \
    -e MYSQL_PASSWORD=$PASS \
    -e MYSQL_RANDOM_ROOT_PASSWORD=true \
    --name $DB_CONTAINER_NAME \
    --rm \
    -p 3306:3306 \
    $DB_CONTAINER_AUTO_TAG

sleep 1m

# does not have wait for db functionality yet
pipenv run python start.py -t -w 180

# docker run \
#     --name grab \
#     -e DATABASE=billboard_charts \
#     -e DB_TYPE=mysql \
#     -e DB_USERNAME=chart \
#     -e DB_HOST=autodb:3306 \
#     -e PASS=temporaryaccess \
#     --rm \
#     --network chart \
#     registry.gitlab.com/joyfulflyer/billboard-grabber python start.py -u -w 180

mkdir $TEMP_DIRECTORY
cd $TEMP_DIRECTORY

docker exec -i $DB_CONTAINER_NAME mysqldump -u $DB_USERNAME --password=$PASS $DATABASE >$FILE_NAME

# docker cleanup
docker stop $DB_CONTAINER_NAME
# docker network rm chart

# build docker container

# create temp docker file
(
    printf "FROM mysql:8.0.21\n\nCOPY $FILE_NAME /docker-entrypoint-initdb.d/" >tempdockerfile
    docker build --pull --rm -f "./tempdockerfile" --tag $DB_CONTAINER_TIERS_TAG .
    docker tag $DB_CONTAINER_TIERS_TAG $DB_CONTAINER_AUTO_TAG
    docker push $DB_CONTAINER_TIERS_TAG
    docker push $DB_CONTAINER_AUTO_TAG
) &

# upload gzipped backup to s3
(
    gzip -k $FILE_NAME
    aws s3 cp $FILE_NAME.gz s3://billboard-viewer-db
    rm $FILE_NAME.gz
) &

wait

#cleanup
cd ..
rm -r $TEMP_DIRECTORY
