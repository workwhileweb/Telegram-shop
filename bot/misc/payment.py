import aiohttp
import json
import math

from aiogram import Bot
from aiogram.types import LabeledPrice
from typing import Optional
from bot.misc import EnvKeys

ZERO_DEC_CURRENCIES = {"JPY", "KRW"}  # без копеек/центов


def rub_to_stars(amount_rub: int) -> int:
    """
    Конвертирует сумму в рублях в целое число звёзд.
    Округляем вверх (ceil), чтобы не занизить списание.
    """
    return int(math.ceil(float(amount_rub) * EnvKeys.STARS_PER_VALUE))


async def send_stars_invoice(
        bot: Bot,
        chat_id: int,
        amount: int,
        title: str = "Пополнение баланса",
        description: str | None = None,
        payload_extra: dict | None = None,
):
    """
    Отправляет инвойс Telegram Stars (currency='XTR', provider_token='').
    total_amount задаётся в наименьших единицах XTR (звёзды * 100).
    """
    stars = rub_to_stars(amount)
    prices = [LabeledPrice(label=f"{stars} ⭐️", amount=stars)]
    payload = {
        "op": "topup_balance_stars",
        "amount_rub": int(amount),
        "stars": stars,
    }
    if payload_extra:
        payload.update(payload_extra)

    await bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description or f"Пополнение на {amount}₽ через Telegram Stars",
        payload=json.dumps(payload),
        provider_token="",  # для Stars должен быть пустым
        currency="XTR",
        prices=prices,
    )


def _minor_units_for(currency: str) -> int:
    return 1 if currency.upper() in ZERO_DEC_CURRENCIES else 100


async def send_fiat_invoice(*, bot, chat_id: int, amount: int,
                            title: str = "Пополнение баланса",
                            description: str = "Оплата через Telegram Payments (карта)"):
    """
    Выставляет инвойс через Telegram Payments (fiat-провайдер).
    amount — сумма (в основных единицах).
    """
    provider_token = EnvKeys.TELEGRAM_PROVIDER_TOKEN
    if not provider_token:
        raise RuntimeError("TELEGRAM_PROVIDER_TOKEN is not set")

    currency = (getattr(EnvKeys, "TELEGRAM_PAY_CURRENCY", None) or "RUB").upper()
    multiplier = _minor_units_for(currency)
    amount_minor = int(amount) * multiplier

    prices = [LabeledPrice(label=f"Пополнение {amount} {currency}", amount=amount_minor)]
    payload = json.dumps({"type": "balance_topup", "amount": int(amount)})

    await bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description,
        payload=payload,
        provider_token=provider_token,
        currency=currency,
        prices=prices,
        request_timeout=60,
    )


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
