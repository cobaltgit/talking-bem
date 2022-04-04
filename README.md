# Talking Ben Discord Bot

This is a simple Discord bot that follows the functionality of the Talking Ben mobile game by Outfit7  
There is no need to install a sidecar database server, so the bot will use little resources  
You must have Python 3.10+ installed on your system to use this bot  

## Installation

Personally, I'd rather you not create a public instance of this bot  
However, for transparency purposes, this source code along with installation instructions have been provided

- Clone this repository into a directory on your machine

``` sh
$ git clone https://github.com/cobaltgit/talking-ben.git
# ...
```

- Install the dependencies

``` sh
$ python3.10 -m pip install pipenv
# ...
$ pipenv install
# ...
```

## Running the Bot

Ensure you have a Discord Developer API application and bot token ready: Instructions can be found [here](https://discordpy.readthedocs.io/en/latest/discord.html)

- Create a config.json file with the following contents

``` json
{
    "token": "bot-token-here",
    "application_id": 123456789876543210
}
```

- To start your instance, run this shell command

``` sh
$ pipenv run start
☎ Talking Ben is ready to take calls
```

## Docker: Alternative Installation

For convenience's sake, a multiarch Docker image of the bot is actively maintained, up to date with the Git `main` branch

### Environment variables

- **TOKEN**: The bot token
- **APPLICATION_ID**: The Discord application ID

### Running the Container

Like the above instructions, ensure you have a Discord Developer API application ID and bot token at hand  
To run using the Docker CLI, you can use this shell command:  

```sh
$ docker run -dit -e TOKEN=bot-token-here -e APPLICATION_ID=123456789876543210 --restart=unless-stopped cobaltdocker/talking-ben-bot
# ...container ID
```

Alternatively, you can use docker-compose:  

```yml
version: "3"
services:
    ben:
        image: cobaltdocker/talking-ben-bot
        environment:
            TOKEN: "bot-token-here"
            APPLICATION_ID: 123456789876543210
```

#### Supported Architectures

This image supports the following architectures, as does its Python base image

```sh
linux/amd64 # x86-64 (64-bit x86)
linux/arm64 # aarch64 (64-bit ARM)
linux/arm/v5 # armv5l (32-bit ARM)
linux/arm/v7 # armv7l/armhf (current 32-bit ARM)
linux/ppc64le # PowerPC 64-bit
linux/s390x # IBM System/390
```