FROM python:alpine AS base

# set /code as the work directory
WORKDIR /code

RUN \
    # update alpine repositories
    apk update \
    # build tools dependencies
    && apk add --no-cache build-base cmake git \
    # mgba dependencies
    && apk add --no-cache libffi-dev elfutils-dev libzip-tools minizip-dev libedit-dev sqlite-dev libepoxy-dev ffmpeg ffmpeg-dev libpng-dev jpeg-dev \
    && pip install cffi

RUN \
    cd /code \
    # clone mgba
    && git clone https://github.com/mgba-emu/mgba.git --branch 0.9 mgba \
    # create build directory
    && mkdir mgba/build \
    # go to the build directory
    && cd mgba/build \
    # configure the build
    && cmake -DBUILD_PYTHON=ON -DBUILD_QT=OFF -DBUILD_SDL=OFF -DUSE_DISCORD_RPC=OFF -DCMAKE_INSTALL_PREFIX:PATH=/usr/local .. \
    # build mGBA
    && make \
    # install mGBA, TODO: is install needed ?
    && make install

# copy poetry config file
COPY ./pyproject.toml /code

RUN \
    cd /code \
    # install poetry
    && pip install poetry \
    # config poetry to not create a .venv
    && poetry config virtualenvs.create false \
    # upgrade pip
    && poetry run pip install --upgrade pip

RUN \
    cd /code/mgba/src/platform/python \
    # install mGBA bindings, TODO: can delete everything else ?
    && BINDIR=/code/mgba/build/include LIBDIR=/code/mgba/build/include python setup.py install

# copy the src files
COPY ./src /code/src

FROM base AS prod
RUN poetry install --no-interaction --no-ansi --no-dev

FROM prod as dev
RUN poetry install --no-interaction --no-ansi

FROM prod AS server
CMD [ "poetry", "run", "python", "src/server.py" ]

FROM prod AS emulator
CMD [ "poetry", "run", "python", "src/emulator.py" ]
