# QUICK_START
   1. Clone project
   2. Create a virtual venv
   3. Install requirements:
       ```
       pip install --upgrade pip
       pip install -r requirements.txt
       ```
   4. [Setup environment variables:](https://stackoverflow.com/questions/42708389/how-to-set-environment-variables-in-pycharm)

      - [TOKEN](https://telegram.me/BotFather)
      - [OWNER_ID](https://telegram.me/myidbot)
      - [CRYPTO_PAY_TOKEN](https://help.send.tg/en/articles/10279948-crypto-pay-api#h_020215e6d7)
      - [TELEGRAM_PROVIDER_TOKEN](https://core.telegram.org/bots/payments#getting-a-token)
      - TELEGRAM_PAY_CURRENCY - the currency for paying the invoice
      - STARS_PER_VALUE - the equivalent of stars per unit of currency
      - CHANNEL_URL - telegram channel link (initially disabled)
      - HELPER_URL - telegram username for help (initially disabled)
      - [GROUP_ID](https://docs.b2core.b2broker.com/how-to-articles/manage-communication-platforms/how-to-get-telegram-chat-group-and-channel-identifiers) -  telegram group ID (initially disabled)
      - REFERRAL_PERCENT - percentage of the referral deposit (initially disabled)
      - RULES - rules for using the bot (initially disabled)
      - PAYMENT_TIME - time allotted for payment

   5. Run run.py

### P.S.
1. Add the bot to the channel and group you have provided and make it an admin
2. To apply latest migration, use 
      ```
      alembic upgrade head
      ```
3. If you want to change the path to BOT_LOGFILE and BOT_AUDITFILE, set it as an environment variable.

### [BACK](../README.md)