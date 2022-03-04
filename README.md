# B00 plays GBA

B00 plays GBA is an interactive emulator made to entertain people during waiting phases, such as during TVn7 pre-shows.

<!-- mettre d'autres images, des screenshots -->

## Built with

### Technologies

- [Python](https://www.python.org/)
- [mGBA](https://mgba.io/)
- [Redis](https://redis.io/)
- [Websockets](https://websockets.readthedocs.io/)
- [Nginx-RTMP](https://hub.docker.com/r/tiangolo/nginx-rtmp/)
- [FFmpeg](https://www.ffmpeg.org)

### Tools

- [Poetry](https://python-poetry.org/)
- [Docker](https://www.docker.com/)
- [Kubernetes](https://kubernetes.io/)
- [Docker-slim](https://dockersl.im/)
- [AGB-buttontest](https://github.com/heroldev/AGB-buttontest)

### [VSCode](https://code.visualstudio.com/)

- [ms-python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Python Docstring Generator](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring)
- [Conventional Commits](https://marketplace.visualstudio.com/items?itemName=vivaxy.vscode-conventional-commits)
- [Remote container](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [EditorConfig](https://marketplace.visualstudio.com/items?itemName=EditorConfig.EditorConfig)
- [Kubernetes](https://marketplace.visualstudio.com/items?itemName=ms-kubernetes-tools.vscode-kubernetes-tools)
- [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)


## Getting started

### Installation

Clone the repository :

```bash
git clone git@git.inpt.fr:fainsil/booplaysgba.git --recursive
```

Build the mGBA python bindings:

```bash
cd booplaysgba
mkdir mgba/build
cd mgba/build
cmake -DBUILD_PYTHON=ON -DBUILD_QT=OFF -DBUILD_SDL=OFF -DUSE_DISCORD_RPC=OFF ..
make
```

Install the dependencies :

```bash
cd ../..
poetry run pip install --upgrade pip
BINDIR=`pwd`/mgba/build/ LIBDIR=`pwd`/mgba/build/ poetry install
```

### Usage

To run locally the server :

```bash
python3 src/server.py
```

To run locally the emulator :

```bash
python3 src/emulator.py
```

## Contributing

This repository is under the [Contributing Covenant](https://www.contributor-covenant.org/) code of conduct. \
See [`CONTRIBUTING.md`](https://git.inpt.fr/fainsil/booplaysgba/-/blob/master/CONTRIBUTING.md) for more information. \
Please use [conventional commits](https://www.conventionalcommits.org/).

## License

Distributed under the [MIT](https://choosealicense.com/licenses/mit/) license.
See [`LICENSE`](https://git.inpt.fr/fainsil/booplaysgba/-/blob/master/LICENSE) for more information.

## Contact

Laurent Fainsin \<[laurentfainsin@protonmail.com](mailto:laurentfainsin@protonmail.com)\>
