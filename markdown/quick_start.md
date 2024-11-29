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
      - [ACCESS_TOKEN](https://pypi.org/project/YooMoney/#access-token)
      - [ACCOUNT_NUMBER](https://pypi.org/project/YooMoney/#account-information)

   5. [Setup config.py](../bot/misc/config.py)
      - CHANNEL_URL - telegram channel link (https://t.me/your_channel)
      - HELPER_URL -  telegram username (@username) for help
      - [GROUP_ID](https://docs.b2core.b2broker.com/how-to-articles/manage-communication-platforms/how-to-get-telegram-chat-group-and-channel-identifiers) -  telegram group ID
      - REFERRAL_PERCENT - percentage of the referral deposit (to disable the referral system, enter 0)
      - PAYMENT_TIME - time allotted for payment
      - RULES - rules for using the bot

   6. Run run.py

### P.S.
to apply latest migration, use 
      ```
      alembic upgrade head
      ```

### [BACK](../README.md)