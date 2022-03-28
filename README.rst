Talking Ben Discord Bot
=======================

| This is a simple Discord bot that follows the functionality of the Talking Ben mobile game by Outfit7  
| There is no need to install a sidecar database server, so the bot will use little resources
| You must have Python 3.10+ installed on your system to use this bot

Installation
------------

Installation is easy! Just follow the below instructions

* Clone this repository into a directory on your machine

.. code:: sh
    
    $ git clone https://github.com/cobaltgit/talking-ben.git

* Install the dependencies

.. code:: sh

    $ python3.10 -m pip install pipenv
    # ...
    $ pipenv install
    # ...

Running the Bot
---------------

**Ensure you have a Discord Developer API application and bot token ready: Instructions can be found `here
<https://discordpy.readthedocs.io/en/latest/discord.html>`_**

* Create a config.json file with the following contents

.. code:: json

    {
        "token": "bot-token-here
        "application_id": 123456789876543210
    }

* To start your instance, run this shell command

.. code:: sh

    $ pipenv run start
    ☎ Talking Ben is ready to take calls