from os import environ
import telebot
import logging

from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = environ.get("BOT_TOKEN") or ""
LOG_LEVEL = int(environ.get("LOG_LEVEL")) or 20

logging.basicConfig(level=LOG_LEVEL)
logging.debug("Bot token: %s", BOT_TOKEN)
logging.debug("Log level: %d", LOG_LEVEL)


try:
    logging.info("Configuring the bot...")
    bot = telebot.TeleBot(BOT_TOKEN)
    logging.info("Done configuring the bot!")
except Exception as e:
    logging.critical("Uncaught exception while configuring the bot", exc_info=e)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


try:
    logging.info("Starting the bot...")
    bot.infinity_polling()
    logging.info("Normally stopping the bot!")
except Exception as e:
    logging.critical("Uncaught exception while running the bot", exc_info=e)