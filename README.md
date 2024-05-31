# `pfmdb`

[![Build](https://github.com/FNNDSC/pfmdb/actions/workflows/build.yml/badge.svg)](https://github.com/FNNDSC/pfmdb/actions/workflows/build.yml)

*a FastAPI REST service that provides web-based interfaces to a mongo server using pfmongo*

## Abstract

`pfmdb` is a FastAPI application that provides REST services accessing a mongo server using `pfmongo` approaches (i.e. a flat shadow collection for faster searching and hashing added to each json document in a collection).


## `pfmdb` Specificities

`pfmdb` is bundled with mongo express in addition to mongo, providing another web-based view into the mongo server. The `pfmdb` API reflects the command subgroup structure of `pfmongo`.

## `pfmdb` Deployment

### local build

To build a local version, clone this repo and then

```bash
docker-compose up

```

The FastAPI service is listening on `:8025` with swagger at `:8025/docs`.

### dockerhub

To use the version available on dockerhub (note, might not be available at time of reading):

```bash
docker pull fnndsc/pfmdb
```

### running

To start the services

```bash
SESSIONUSER=localuser
docker run --gpus all --privileged          \
        --env SESSIONUSER=$SESSIONUSER      \
        --name pfmdb --rm -it -d             \
        -p 2024:2024                        \
        local/pfmdb /start-reload.sh
```

To start with source code debugging and live refreshing:

```bash
SESSIONUSER=localuser
docker run --gpus all --privileged          \
        --env SESSIONUSER=$SESSIONUSER      \
        --name pfmdb --rm -it -d             \
        -p 2024:2024                        \
        -v $PWD/pfmdb:/app:ro
        local/pfmdb /start-reload.sh
```

(note if you pulled from dockerhub, use `fnndsc/pfmdb` instead of `local/pfmdb`)


_-30-_
