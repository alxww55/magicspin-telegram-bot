[![Codacy Badge](https://app.codacy.com/project/badge/Grade/5bbf8c093dfe4f6b9fdde16f98b8159e)](https://app.codacy.com/gh/alxww55/magicspin-telegram-bot/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

# 🎰 Magic Spin - Slot machine simulator

A lightweight and fun Telegram bot that brings the classic slot machine experience directly to your chat.
Spin the reels, collect coins, and enjoy a simple casino-style game built with modern Python technologies.

![MagicSpin screenshots](https://github.com/alxww55/magicspin-telegram-bot/blob/main/magispin.png)

## Technology stack:

- [aiogram](https://github.com/aiogram/aiogram) - asynchronous framework for Telegram Bot API
- [redis-py](https://github.com/redis/redis-py) - caching for user sessions
- [sqlalchemy](https://github.com/sqlalchemy/sqlalchemy) - ORM toolkit
- [postgresql](https://www.postgresql.org) - persistent data storage

## Features:

- Auto-generated captcha on /start
- Self-implemented strict Rate Limiting with blacklisting and continiuosly checking
- User Sessions caching with redis
- Pesistent Storage with ORM-interface

## Usage

### Individual config

1. Search for **@BotFather** in Telegram, create a bot, and copy your API Token.
2. Clone this repository.
3. Open `.env.example` and fill it as follows:

```
BOT_API_KEY: Your API Token for the bot

REDIS_USER: Username
REDIS_PASSWORD: Password
REDIS_HOST: IP of your PC in your network, e.g., 172.0.0.12 or 192.168.1.2
REDIS_PORT: Port for Redis, default = 6379

POSTGRES_USER: Username
POSTGRES_PASSWORD: Password
POSTGRES_HOST: IP of your PC in your network, e.g., 172.0.0.12 or 192.168.1.2
POSTGRES_PORT: Port for PostgreSQL, default = 5432
POSTGRES_DB: Database name

RATE_LIMITING_PERIOD: How many seconds should be monitored
MESSAGES_PER_PERIOD: How many messages a user is allowed to send during the rate-limiting period
```

4. Rename the file to `.env`.
5. Open `redis.conf.example` and fill it as follows:

```
user {REDIS_USER from .env} on >{REDIS_PASSWORD from .env} {allowed commands, default - allcomands} {allowed commands, default - allkeys}
```

so that looks like: `user redis_usr on >my_strong_password allcommands allkeys`.

6. Rename the file to `redis.conf`.

### Run with Docker Compose

1. Open a terminal and navigate to the folder where the project's `docker-compose.yaml` is located.
2. Execute: `docker compose build`
3. Execute `docker compose up -d`

### Ready to play

Now open Telegram, start your bot, and have a nice game!

### Stopping an app

Please ensure you are stopping an app with `docker compose stop`. Using of `docker compose down` can lead to data loss.

## Disclaimer

This bot uses demo coins — not real money. Project was built for mastering skill and demo/portfolio purposes only.
