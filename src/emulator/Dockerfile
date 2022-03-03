FROM python:alpine AS base

# set /src as the work directory
WORKDIR /src

# update alpine repositories
RUN apk update
# build tools dependencies
RUN apk add --no-cache build-base cmake git
# mgba dependencies
RUN apk add --no-cache libffi-dev elfutils-dev libzip-tools minizip-dev libedit-dev sqlite-dev libepoxy-dev ffmpeg ffmpeg-dev libpng-dev jpeg-dev
RUN pip install cffi

# clone mgba
RUN git clone https://github.com/mgba-emu/mgba.git
# create build directory
WORKDIR /src/mgba/build/
# configure the build
RUN cmake -DBUILD_PYTHON=ON -DBUILD_QT=OFF -DBUILD_SDL=OFF -DUSE_DISCORD_RPC=OFF -DCMAKE_INSTALL_PREFIX:PATH=/usr/local ..
# build mGBA
RUN make
# install mGBA, TODO: is install needed ?
RUN make install

WORKDIR /src
# upgrade pip
RUN pip install --upgrade pip
# copy requirements.txt for installation
COPY requirements.txt /src/
# install python dependencies
RUN pip install -r /src/requirements.txt
# remove requirements.txt
RUN rm /src/requirements.txt

# install mGBA bindings, TODO: can delete everything else ?
WORKDIR /src/mgba/src/platform/python
RUN BINDIR=/src/mgba/build/include LIBDIR=/src/mgba/build/include python setup.py install

# copy the src files
WORKDIR /src
COPY *.py /src/

# run the application
CMD ["python", "/src/main.py" ]
