# QUICK_START

## Environment Variables

The application requires the following environment variables:

<details>
<summary><b>Telegram</b></summary>

| Variable                                   | Description                                  |
|--------------------------------------------|----------------------------------------------|
| [BOT_TOKEN](https://telegram.me/BotFather) | Telegram Bot API token for bot functionality |
| [OWNER_ID](https://telegram.me/myidbot)    | Owner's ID in Telegram                       |

</details>

<details>
<summary><b>Payments</b></summary>

| Variable                                                                                  | Description                                                                                                                      |
|-------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| [TELEGRAM_PROVIDER_TOKEN](https://core.telegram.org/bots/payments#getting-a-token)        | Provider's token for accepting payments                                                                                          |
| [CRYPTO_PAY_TOKEN](https://help.send.tg/en/articles/10279948-crypto-pay-api#h_020215e6d7) | CryptoPay API token (initially disabled)                                                                                         |
| STARS_PER_VALUE                                                                           | the equivalent of stars per unit of currency (to disable this payment method, set 0)                                             |
| PAY_CURRENCY                                                                              | the currency for paying the invoice (for Crypto Bot and Telegram Pay) and the displayed currency in the bot (examples: RUB, USD) |
| REFERRAL_PERCENT                                                                          | percentage of the referral deposit (initially disabled)                                                                          |
| PAYMENT_TIME                                                                              | PAYMENT_TIME - time allotted for payment (CryptoPay) in seconds (initially 1800 sec)                                             |
| MIN_AMOUNT                                                                                | minimum amount for crediting (initially 20)                                                                                      |
| MAX_AMOUNT                                                                                | maximum amount for crediting (initially 10_000)                                                                                  |

</details>

<details>
<summary><b>Links / UI</b></summary>

| Variable    | Description                                                                                                                            |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------|
| CHANNEL_URL | Telegram channel link. Notifications about assortment updates will occur there. (only works with public channels) (initially disabled) |
| HELPER_ID   | Helper's ID in Telegram                                                                                                                |
| RULES       | rules for using the bot (initially disabled)                                                                                           |

</details>

<details>
<summary><b>Locale & logs</b></summary>

| Variable      | Description                                                                                                                   |
|---------------|-------------------------------------------------------------------------------------------------------------------------------|
| BOT_LOCALE    | localization language (options: ru, en) (initially ru)                                                                        |
| BOT_LOGFILE   | If you want to change the path to the BOT_LOGFILE, set it as an environment variable (initially in the root of the project)   |
| BOT_AUDITFILE | If you want to change the path to the BOT_AUDITFILE, set it as an environment variable (initially in the root of the project) |
| LOG_TO_STDOUT | logging in the console (initially enabled) (options: 1, 0)                                                                    |
| LOG_TO_FILE   | logging to files (BOT_LOGFILE, BOT_AUDITFILE) (initially enabled) (options: 1, 0)                                             |
| DEBUG         | DEBUG mode for logging (initially disabled) (options 1, 0)                                                                    |

</details>

<details>
<summary><b>Database (for Docker)</b></summary>

| Variable          | Description                                                                                           |
|-------------------|-------------------------------------------------------------------------------------------------------|
| POSTGRES_DB       | PostgreSQL database name                                                                              |
| POSTGRES_USER     | PostgreSQL username (initially postgres)                                                              |
| POSTGRES_PASSWORD | PostgreSQL password.                                                                                  |
| DB_PORT           | PostgreSQL port (initially 5432)                                                                      |
| DB_DRIVER         | Driver for database (initially postgresql+psycopg2) (Dont change if you dont know what you are doing) |

</details>


<details>
<summary><b>Database (for manual deploy)</b></summary>

[Setup](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) [DATABASE_URL](../bot/misc/env.py) (supports:
PostgreSQL - preferably, MySQL, sqlite3, etc)
</details>

## How to deploy with [docker](https://www.docker.com/)

1. Clone project
2. Create a `.env` file in the root directory with all the environment variables listed above

    ```
    mv .env.example .env
    ```

3. Run the bot:

    ```
    docker compose up -d --build bot
    ```

## How to deploy manually

1. Clone project
2. Create a virtual venv
3. Install requirements:
    ```
    pip install --upgrade pip
    pip install -r requirements.txt
    ```
4. [Setup environment variables listed above](https://stackoverflow.com/questions/42708389/how-to-set-environment-variables-in-pycharm)

5. Run run.py

### P.S.

1. Add the bot to the channel you provided and make it an admin.
2. To apply latest migration, use:
    <details>
    <summary><b>Docker</b></summary>

    ```
    docker compose run --rm bot alembic upgrade head
    ```
    </details>

    <details>
    <summary><b>Manual deploy</b></summary>

    ```
    alembic upgrade head
    ```
    </details>

### [BACK](../README.md)