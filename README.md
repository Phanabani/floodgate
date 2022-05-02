# Floodgate

[![release](https://img.shields.io/github/v/release/phanabani/floodgate)](https://github.com/phanabani/floodgate/releases)
[![license](https://img.shields.io/github/license/phanabani/floodgate)](LICENSE)

A Discord bot that allows messages in channels for only a specified amount of time.

## Table of Contents

- [Install](#install)
- [Usage](#usage)
- [Config](#config)
- [Commands](#commands)
- [Developers](#developers)
- [License](#license)

## Install

### Prerequisites

- [Poetry](https://python-poetry.org/docs/#installation) – dependency manager
- (Optional) pyenv – Python version manager
    - [pyenv](https://github.com/pyenv/pyenv) (Linux, Mac)
    - [pyenv-win](https://github.com/pyenv-win/pyenv-win) (Windows)
- (Optional) [PM2](https://pm2.keymetrics.io/docs/usage/quick-start) – process manager

### Install Floodgate

To get started, clone the repo.

```shell
git clone https://github.com/phanabani/floodgate.git
cd floodgate
```

Install the dependencies with Poetry. Floodgate requires Python 3.9.6+.

```shell
poetry install --no-root --no-dev
```

## Usage

### Set up configuration

See [Config](docs/config.md) for detailed information about setting up the
config file.

### Running Floodgate

#### Basic

In the top level directory, simply run Floodgate as a Python module with Poetry.

```shell script
poetry run python -m floodgate
```

#### With PM2

You can run the bot as a background process using PM2. Ensure you've followed
the virtual environment setup described above, then simply run the following
command in Floodgate's root directory:

```shell script
pm2 start
```

This starts the process as a daemon using info from [ecosystem.config.js](ecosystem.config.js).

### Inviting Floodgate to your Discord server

Floodgate requires the following permissions to run normally:

- Send messages
- Send messages in threads
- Manage messages (to delete messages in closed gate channels)

## Commands

See [Commands](docs/commands.md) for info about Floodgate's commands.

## Developers

### Installation

Follow the installation steps in [install](#install) and use Poetry to 
install the development dependencies:

```bash
poetry install --no-root
```

## License

[MIT © Phanabani.](LICENSE)
