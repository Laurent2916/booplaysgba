apk update
apk add build-base cmake git vim
apk add libffi-dev elfutils-dev libzip-tools minizip-dev libedit-dev sqlite-dev libepoxy-dev ffmpeg-dev libpng-dev jpeg-dev
pip install poetry cffi
mkdir /code
cd /code
vim pyproject.toml # copy le pyproject.tom manuel
git clone https://github.com/mgba-emu/mgba.git mgba
mkdir mgba/build
cd mgba/build
cmake -DBUILD_PYTHON=ON -DBUILD_QT=OFF -DBUILD_SDL=OFF -DUSE_DISCORD_RPC=OFF -DCMAKE_INSTALL_PREFIX:PATH=/usr/local/ ..
make
make install
cd /code/mgba/src/platform/python/
BINDIR=/code/mgba/build/include/ LIBDIR=/code/mgba/build/include/ python setup.py install
cd /code/
poetry install
