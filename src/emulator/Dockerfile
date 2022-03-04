FROM python:alpine AS base

# set /src as the work directory
WORKDIR /src

# update alpine repositories
RUN apk update
# build tools dependencies
RUN apk add --no-cache build-base cmake git
# mgba dependencies
RUN apk add --no-cache libffi-dev ffmpeg ffmpeg-dev libpng-dev jpeg-dev
RUN pip install --user cffi

# clone mgba
RUN git clone https://github.com/mgba-emu/mgba.git
# create build directory
WORKDIR /src/mgba/build/
# configure the build
RUN cmake \
    -DBUILD_PYTHON=ON \
    -DBUILD_QT=OFF \
    -DBUILD_SDL=OFF \
    -DBUILD_GL=OFF \
    -DBUILD_GLES2=OFF \
    -DBUILD_GLES3=OFF \
    -DBUILD_SHARED=OFF \
    -DUSE_DEBUGGERS=ON \
    -DUSE_DISCORD_RPC=OFF \
    -DUSE_EDITLINE=OFF \
    -DUSE_ELF=OFF \
    -DUSE_EPOXYNG=OFF \
    -DUSE_FFMPEG=ON \
    -DUSE_GDB_STUB=ON \
    -DUSE_LIBZIP=OFF \
    -DUSE_LZMA=OFF \
    -DUSE_MINIZIP=OFF \
    -DUSE_PNG=ON \
    -DUSE_SQLITE3=OFF \
    -DUSE_ZLIB=OFF \
    -DCMAKE_INSTALL_PREFIX:PATH=/usr/local \
    ..
# build mGBA
RUN make
# install mGBA
RUN make install

WORKDIR /src
# upgrade pip
RUN pip install --upgrade pip
# copy requirements.txt for installation
COPY requirements.txt /src/
# install python dependencies
RUN pip install --user -r /src/requirements.txt

# install mGBA bindings
WORKDIR /src/mgba/src/platform/python
RUN BINDIR=/src/mgba/build/include LIBDIR=/src/mgba/build/include python setup.py install --user

FROM python:alpine

# install required libraries
RUN apk add --no-cache ffmpeg

# copy necessary mgba files
COPY --from=base /root/.local /root/.local
COPY --from=base /usr/local/lib/libmgba.so* /usr/local/lib/

# copy the src files
WORKDIR /src
COPY *.py /src/

# run the application
CMD ["python", "/src/main.py" ]
