"""
Telegram-бот для удаления ссылок на Яндекс.Музыку от конкретного пользователя
+ после удаления отправляет одно предупреждение (случайный текст из 10 вариантов)
"""

import asyncio
import logging
import os
import re
import random

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# ==============================
# ПОЛНОЕ ОТКЛЮЧЕНИЕ ЛОГИРОВАНИЯ
# ==============================
logging.disable(logging.CRITICAL)
logger = logging.getLogger(__name__)

# Импортируем настройки из config.py
try:
    from config import BOT_TOKEN as CONFIG_BOT_TOKEN, TARGET_USER_ID as CONFIG_TARGET_USER_ID
except ImportError:
    CONFIG_BOT_TOKEN = None
    CONFIG_TARGET_USER_ID = 0

# Получаем токен: сначала из переменной окружения, затем из config.py
BOT_TOKEN = os.getenv('BOT_TOKEN') or CONFIG_BOT_TOKEN

# ID пользователя: сначала из переменной окружения, затем из config.py
env_user_id = os.getenv('TARGET_USER_ID')
if env_user_id:
    TARGET_USER_ID = int(env_user_id)
else:
    TARGET_USER_ID = CONFIG_TARGET_USER_ID

# Тип беседы (группа или супергруппа)
CHAT_TYPE = ['group', 'supergroup']

# Регулярное выражение для поиска ссылок на Яндекс.Музыку
YANDEX_MUSIC_PATTERN = re.compile(
    r'(?:https?://)?(?:www\.)?music\.yandex\.(?:ru|com)',
    re.IGNORECASE
)

# 10 сообщений — одно случайное на каждое удаление
WARNING_MESSAGES = [
    "Димончик, пожалуйста, не присылай больше музыку",
    "Дим, давай без музыкальных ссылок 🙏",
    "Димон, стоп музло, пожалуйста 😄",
    "Дим, тут не кидаем Яндекс.Музыку — спасибо!",
    "Димончик, по-дружески: без музыкальных ссылок 👌",
    "Дим, не надо музыку сюда, ок? 🙂",
    "Димон, давай держать чат без муз-ссылок 🎵🚫",
    "Дим, пожалуйста, больше не присылай ссылки на музыку 🙏",
    "Димончик, давай без music.yandex — договорились? 😉",
    "Дим, музыкальные ссылки удаляются автоматически — лучше не надо 🙂",
]


async def delete_yandex_music_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message:
        return

    # Проверяем, что это группа или супергруппа
    if message.chat.type not in CHAT_TYPE:
        return

    # Проверяем отправителя
    if not message.from_user:
        return

    if message.from_user.id != TARGET_USER_ID:
        return

    # Проверяем ссылки
    has_yandex_link = False

    # entities в тексте
    if message.entities and message.text:
        for entity in message.entities:
            if entity.type == "text_link" and entity.url:
                if YANDEX_MUSIC_PATTERN.search(entity.url):
                    has_yandex_link = True
                    break
            elif entity.type == "url":
                link_text = message.text[entity.offset:entity.offset + entity.length]
                if YANDEX_MUSIC_PATTERN.search(link_text):
                    has_yandex_link = True
                    break

    # caption_entities
    if not has_yandex_link and message.caption_entities and message.caption:
        for entity in message.caption_entities:
            if entity.type == "text_link" and entity.url:
                if YANDEX_MUSIC_PATTERN.search(entity.url):
                    has_yandex_link = True
                    break
            elif entity.type == "url":
                link_text = message.caption[entity.offset:entity.offset + entity.length]
                if YANDEX_MUSIC_PATTERN.search(link_text):
                    has_yandex_link = True
                    break

    # запасная проверка по всему тексту
    if not has_yandex_link:
        text = message.text or message.caption
        if text and YANDEX_MUSIC_PATTERN.search(text):
            has_yandex_link = True

    # Если ссылка найдена — удаляем
    if has_yandex_link:
        deleted = False

        for attempt in range(3):
            try:
                await context.bot.delete_message(
                    chat_id=message.chat.id,
                    message_id=message.message_id
                )
                deleted = True
                break
            except Exception:
                if attempt < 2:
                    await asyncio.sleep(0.3)

        # После успешного удаления — отправляем предупреждение
        if deleted:
            warn_text = random.choice(WARNING_MESSAGES)
            try:
                await context.bot.send_message(
                    chat_id=message.chat.id,
                    text=warn_text
                )
            except Exception:
                pass


def main() -> None:
    if not BOT_TOKEN or TARGET_USER_ID == 0:
        return

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(
        MessageHandler(filters.ALL, delete_yandex_music_links)
    )

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
