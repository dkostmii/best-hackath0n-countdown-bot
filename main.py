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


def read_json(json_filename: str) -> dict:
    try:
        with open(json_filename, mode="r") as f:
            result = json.load(f)

        if not isinstance(result, dict):
            raise Exception("Expected result to be dict")

        return result
    except OSError as e:
        logging.error("Error reading JSON file %s", json_filename, exc_info=e)
    except Exception as e:
        logging.critical("Uncaught exception while reading JSON file %", json_filename, exc_info=e)


data = read_json("data.json")
captions = read_json("captions.json")


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