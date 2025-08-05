from yoomoney import Quickpay, Client
import random
import aiohttp
from typing import Optional
from bot.misc import EnvKeys


def quick_pay(amount, user_id):
    bill = Quickpay(
        receiver=EnvKeys.ACCOUNT_NUMBER,
        quickpay_form="shop",
        targets="Sponsor",
        paymentType="SB",
        sum=amount,
        label=str(user_id) + '_' + str(random.randint(1000000000, 9999999999))
    )
    label = bill.label
    url = bill.base_url
    return label, url


async def check_payment_status(label: str):
    client = Client(EnvKeys.ACCESS_TOKEN)
    history = client.operation_history(label=label)
    for operation in history.operations:
        return operation.status


class CryptoPayAPI:
    def __init__(self):
        self.token = EnvKeys.CRYPTO_PAY_TOKEN
        self.base_url = "https://pay.crypt.bot/api"

    async def _request(self, method: str, params: dict) -> dict:
        headers = {"Crypto-Pay-API-Token": self.token}
        url = f"{self.base_url}/{method}"

        if method.startswith("get"):
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as resp:
                    resp.raise_for_status()
                    return await resp.json()
        else:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=params, headers=headers) as resp:
                    resp.raise_for_status()
                    return await resp.json()

    async def create_invoice(
            self,
            amount: float,
            currency: str = "RUB",
            accepted_assets: str = "TON,USDT",
            payload: Optional[str] = None,
            description: Optional[str] = None,
            hidden_message: Optional[str] = None,
            expires_in: int = 1800,
    ) -> dict:
        params = {
            "currency_type": "fiat",
            "fiat": currency,
            "amount": str(amount),
            "accepted_assets": accepted_assets,
            "expires_in": expires_in,
        }
        if payload:
            params["payload"] = payload
        if description:
            params["description"] = description
        if hidden_message:
            params["hidden_message"] = hidden_message

        response = await self._request("createInvoice", params)
        return response.get("result") or {}

    async def get_invoice(self, invoice_id: str) -> dict:
        params = {"invoice_ids": invoice_id}
        res = await self._request("getInvoices", params)
        items = res.get("result", {}).get("items")
        return items[0] if items else {}
