FROM python:alpine

# set /code as the work directory
WORKDIR /code

RUN \
    # update alpine repositories
    apk update \
    # build tools dependencies
    && apk add build-base cmake git \
    # mgba dependencies
    && apk add libffi-dev elfutils-dev libzip-tools minizip-dev libedit-dev sqlite-dev libepoxy-dev ffmpeg ffmpeg-dev libpng-dev jpeg-dev \
    # install poetry and cffi deps for mgba
    && pip install poetry cffi

# copy poetry config files
COPY ./pyproject.toml /code

RUN \
    cd /code \
    # clone mgba
    && git clone https://github.com/mgba-emu/mgba.git mgba \
    # create build directory
    && mkdir mgba/build \
    # go to the build directory
    && cd mgba/build \
    # configure the build
    && cmake -DBUILD_PYTHON=ON -DBUILD_QT=OFF -DBUILD_SDL=OFF -DUSE_DISCORD_RPC=OFF -DCMAKE_INSTALL_PREFIX:PATH=/usr/local .. \
    # build mGBA
    && make \
    # install mGBA
    && make install

RUN \
    cd /code/mgba/src/platform/python \
    # install mGBA bindings
    && BINDIR=/code/mgba/build/include LIBDIR=/code/mgba/build/include python setup.py install

RUN \
    # go to the workdir
    cd /code/ \
    # # config poetry to not create a .venv
    && poetry config virtualenvs.create false \
    # # upgrade pip
    && poetry run pip install --upgrade pip \
    # install poetry
    && poetry install --no-interaction --no-ansi --no-dev

# copy the src files
COPY ./src /code/src
COPY ./roms/pokemon.gba /code/roms/pokemon.gba
