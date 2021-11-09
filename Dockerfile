FROM python:alpine AS base

# set /code as the workdirectory
WORKDIR /code

RUN \
    # update alpine repositories
    apk update \
    # build tools dependencies
    && apk add build-base cmake git \
    # mgba dependencies
    && apk add libffi-dev elfutils-dev libzip-tools minizip-dev libedit-dev sqlite-dev libepoxy-dev ffmpeg-dev libpng-dev \
    # install poetry and cffi deps for mgba
    && pip install poetry cffi

RUN \
    cd /code \
    # clone mgba
    && git clone https://github.com/mgba-emu/mgba.git mgba \
    # create build directory
    && mkdir mgba/build \
    # go to the build directory
    && cd mgba/build \
    # configure the build
    && cmake -DBUILD_PYTHON=ON -DBUILD_QT=OFF -DBUILD_SDL=OFF -DUSE_DISCORD_RPC=OFF .. \
    # build mGBA
    && make

# copy poetry config files
COPY ./poetry.lock ./pyproject.toml /code/

RUN \
    # go to the workdir
    cd /code/ \
    # config poetry to not create a .venv
    && poetry config virtualenvs.create false \
    # upgrade pip
    && poetry run pip install --upgrade pip \
    # install poetry
    && BINDIR=/code/mgba/build/ LIBDIR=/code/mgba/build/ poetry install --no-interaction --no-ansi --no-dev

# stuck at poetry install !
# elfutils-dev for libelf
# libzip-tools || libzip-dev for libzip
# minizip-dev for minizip
# libedit-dev for libedit
# sqlite-dev for sqlite3
# libepoxy-dev for expoxy
# ffmpeg-dev for libavcodec
# libpng-dev for png
# technique d'enlever le -b et de faire setup.py install fonctionne

# copy the src files
COPY ./src /code/

# create server image
FROM base as server
CMD [ "python", "/code/server.py" ]

# create emulator image
FROM base as emulator
CMD [ "python", "/code/emulator.py" ]
