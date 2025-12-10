import asyncio

from faststream import FastStream, AckPolicy
from faststream.kafka import KafkaBroker, KafkaMessage

from app.config import settings
from app.schemas import BrokerMessageSchema

MAX_RETRIES = 3
RETRY_DELAY = 3

TELEGRAM_API_URL = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
GET_CHAT_URL = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getChat"
broker = KafkaBroker(settings.BROKER_KAFKA_HOST)

app = FastStream(broker)


@broker.subscriber(
    "transaction_notification",
    group_id="transaction_notification",
    ack_policy=AckPolicy.MANUAL,
    auto_offset_reset="earliest",
)
async def notify_handler(message: BrokerMessageSchema, msg: KafkaMessage):
    # читаем число попыток
    print(f"[Получено сообщение] Попытка: {message.retries}, данные: {message}")

    try:
        # Имитируем ошибку
        if message.amount % 2 != 0:
            raise RuntimeError("Ошибка отправки уведомления")
        await send_telegram_message(message.user_id_to_telegram_send_massage,
                                    f"Вы получули деньги от типа {await get_telegram_user_info(message.user_id_from_telegram_send_massage)}")
        await send_telegram_message(message.user_id_from_telegram_send_massage,
                                    f"Вы вы отправили  деньги типy {await get_telegram_user_info(message.user_id_from_telegram_send_massage)}")
        print("Уведомление отправлено успешно!")
        await msg.ack()
        return

    except RuntimeError as e:
        print(f"Ошибка обработки: {e}")
        if message.retries + 1 >= MAX_RETRIES:
            print("❌ Лимит попыток! Сообщение зафиксировано.")
            # Тут можно подумать а отдельном топике или чето подобное
            await msg.ack()
            return
        # готовим новое сообщение
        message.retries += 1
        print(f"⏳ Retry #{message.retries} через {RETRY_DELAY} сек...")

        # публикуем заново сообщение в ту же тему,
        # с увеличенным счётчиком попыток
        await broker.publish(message, "transaction_notification")

        # ACK old message, otherwise Kafka will repeat it forever
        await msg.ack()


import aiohttp

BOT_TOKEN = "YOUR_TOKEN"


async def get_telegram_user_info(chat_id: int | str):
    url = GET_CHAT_URL

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params={"chat_id": chat_id}) as resp:
            data = await resp.json()
            if not data.get("ok"):
                raise RuntimeError(f"Telegram API error: {data}")
            return data["result"].get("username")


async def send_telegram_message(chat_id: int | str, text: str):
    async with aiohttp.ClientSession() as session:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"  # или Markdown
        }

        async with session.post(TELEGRAM_API_URL, json=payload) as resp:
            data = await resp.json()
            if not data.get("ok"):
                raise RuntimeError(f"Telegram API error: {data}")
            return data


if __name__ == "__main__":
    asyncio.run(app.run())
