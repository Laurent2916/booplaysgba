0 apk update
1 apk add build-base cmake git
2 apk add libffi-dev elfutils-dev libzip-tools minizip-dev libedit-dev sqlite-dev libepoxy-dev ffmpeg-dev libpng-dev
3 pip install poetry cffi
4 mkdir /code
5 cd /code
6 git clone https://github.com/mgba-emu/mgba.git mgba
7 mkdir mgba/build
8 cd mgba/build
9 cmake -DBUILD_PYTHON=ON -DBUILD_QT=OFF -DBUILD_SDL=OFF -DUSE_DISCORD_RPC=OFF ..
10 make
11 apk add vim
12 vim
13 vim pyproject.tom
14 vim pyproject.toml
15 cd /code
16 poetry config virtualenvs.create false
17 poetry run pip install --upgrade pip
18 vim pyproject.toml
19 poetry run pip install --upgrade pip
20 BINDIR=/code/mgba/build/ LIBDIR=/code/mgba/build/ poetry install --no-interaction --no-ansi --no-dev
21 which python
22 ls /usr/local
23 cmake -DBUILD_PYTHON=ON -DBUILD_QT=OFF -DBUILD_SDL=OFF -DUSE_DISCORD_RPC=OFF -DCMAKE_INSTALL_PREFIX:PATH=/usr/local
24 cmake -DBUILD_PYTHON=ON -DBUILD_QT=OFF -DBUILD_SDL=OFF -DUSE_DISCORD_RPC=OFF -DCMAKE_INSTALL_PREFIX:PATH=/usr/local ..
25 cmake -DBUILD_PYTHON=ON -DBUILD_QT=OFF -DBUILD_SDL=OFF -DUSE_DISCORD_RPC=OFF -DCMAKE_INSTALL_PREFIX:PATH=/usr/local/ ..
26 cd mgba/build
27 cmake -DBUILD_PYTHON=ON -DBUILD_QT=OFF -DBUILD_SDL=OFF -DUSE_DISCORD_RPC=OFF -DCMAKE_INSTALL_PREFIX:PATH=/usr/local/ ..
28 make
29 cd /code/
30 BINDIR=/code/mgba/build/ LIBDIR=/code/mgba/build/ poetry install
31 poetry install
32 cd mgba/src/platform/python/
33 python setup.py install
34 BINDIR=/code/mgba/build/ LIBDIR=/code/mgba/build/ python setup.py install
35 BINDIR=/code/mgba/build/ LIBDIR=/code/mgba/build/ python setup.py installfind
36 find
37 find / | grep flags.h
38 BINDIR=/code/mgba/build/include/ LIBDIR=/code/mgba/build/include/ python setup.py installfind
39 BINDIR=/code/mgba/build/include/ LIBDIR=/code/mgba/build/include/ python setup.py install
40 cd ../../..
41 cd build
42 make install
43 mgba
44 cd ..
45 cd src/platform/python/
46 BINDIR=/code/mgba/build/include/ LIBDIR=/code/mgba/build/include/ python setup.py install
47 history
