# B00 plays GBA

## Built with

- [Python](https://editorconfig.org/)
- [VS Code](https://code.visualstudio.com/)
- [Websockets](https://websockets.readthedocs.io/)
- [mGBA](https://mgba.io/)
- [AGB-buttontest](https://github.com/heroldev/AGB-buttontest)

## Getting started

### Prerequisites

[Poetry](https://python-poetry.org/) should manage every dependencies for you. \
It is recommended to use [VS Code](https://code.visualstudio.com/) with these extensions :

- [ms-python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

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
cmake -DBUILD_PYTHON=ON -DBUILD_QT=OFF -DBUILD_SDL=OFF ..
make
```

Install the dependencies :

```bash
poetry install
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

To access the remote controller :

```bash
firefox src/client.py
```

## Contributing

This repository is under the [Contributing Covenant](https://www.contributor-covenant.org/) code of conduct.
See [`CONTRIBUTING.md`](https://git.inpt.fr/fainsil/booplaysgba/-/blob/master/CONTRIBUTING.md) for more information.\
Please use [conventional commits](https://www.conventionalcommits.org/).

## License

Distributed under the [MIT](https://choosealicense.com/licenses/mit/) license.
See [`LICENSE`](https://git.inpt.fr/fainsil/booplaysgba/-/blob/master/LICENSE) for more information.

## Contact

Laurent Fainsin \<[laurentfainsin@protonmail.com](mailto:laurentfainsin@protonmail.com)\>
