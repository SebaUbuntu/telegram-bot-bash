# HomeBot, a modular Telegram bot, written in Python

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/2cadab25a04c42779f3203b4a61bd6ef)](https://app.codacy.com/gh/SebaUbuntu/HomeBot?utm_source=github.com&utm_medium=referral&utm_content=SebaUbuntu/HomeBot&utm_campaign=Badge_Grade)

## How to use it

-   Execute `pip3 install .` to install all the dependencies
-   Copy `example_config.env` to `config.env`
-   Put a bot token in `config.env`
-   Edit additional variables in `config.env`
-   Launch the bot by typing

```bash
python3 -m homebot
```

## Features

-   Module-based, so you can add and remove modules as you like
-   Easy to understand
-   It uses python-telegram-bot, one of the most used Telegram bot API library

## Modules included

-   weather | Get weather updates of a city
-   speedtest | Test bot's Internet connection speed
-   ci | Automated CI system, you can trigger AOSP custom ROMs and custom recoveries building, with progress updating
-   cowsay
-   And more...

## Wiki

Want to see how this bot works or you want to create a module for this bot?

Head over to [the wiki](https://github.com/SebaUbuntu/HomeBot/wiki) for more informations
