from datetime import datetime, timedelta
import logging
from os import environ

from dotenv import load_dotenv
import telebot

from pluralize import pluralize
from read_json import ReadJSONException, read_json

load_dotenv()
BOT_TOKEN = environ.get("BOT_TOKEN") or environ.get("APPSETTING_BOT_TOKEN") or ""
LOG_LEVEL = int(environ.get("LOG_LEVEL") or environ.get("APPSETTING_LOG_LEVEL") or "20")
ENV = environ.get("ENV") or environ.get("APPSETTING_ENV") or ""
WEBHOOK_DOMAIN = environ.get("WEBHOOK_DOMAIN") or environ.get("APPSETTING_WEBHOOK_DOMAIN") or "127.0.0.1"
WEBHOOK_PORT = int(environ.get("WEBHOOK_PORT") or environ.get("APPSETTING_WEBHOOK_PORT") or "80")

is_dev_env = ENV == "dev"

logging.basicConfig(level=LOG_LEVEL)
logging.debug("Is Development: %s", is_dev_env)
logging.debug("Bot token: %s", BOT_TOKEN)
logging.debug("Log level: %d", LOG_LEVEL)


try:
    logging.info("Reading data...")

    config = read_json("config.dev.json" if is_dev_env else "config.json")
    data = config["data"]

    if not isinstance(data, dict):
        raise ReadJSONException("config.json", "Expected data to be object")

    captions = read_json("captions.json")
    logging.info("Done reading data!")
except ReadJSONException as e:
    logging.error("Error while reading config and captions", exc_info=e)
    exit(1)
except Exception as e:
    logging.critical("Uncaught exception while reading config and captions", exc_info=e)
    exit(1)


try:
    logging.info("Configuring the bot...")
    bot = telebot.TeleBot(BOT_TOKEN)
    logging.info("Done configuring the bot!")
except Exception as e:
    logging.critical("Uncaught exception while configuring the bot", exc_info=e)
    exit(1)


markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
button = telebot.types.KeyboardButton(captions["button"])
markup.add(button)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, captions["start"], reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == captions["button"])
def button_handler(message):
    countdown_dt = data["countdown_dt_iso"]
    countdown_dt = datetime.fromisoformat(countdown_dt)
    tz = countdown_dt.tzinfo
    now_dt = datetime.now(tz=tz)
    now_weekday = captions["weekday"][now_dt.weekday()]
    now_time_hh_mm = now_dt.strftime("%H:%M")

    countdown_dt = countdown_dt.replace(second=0, microsecond=0)
    now_dt = now_dt.replace(second=0, microsecond=0)

    if countdown_dt < now_dt:
        progress_timeout = timedelta(hours=24)
        progress_timeout_min = int(progress_timeout.total_seconds() / 60)

        diff = now_dt - countdown_dt
        diff_min = int(diff.total_seconds() / 60)

        if diff_min <= progress_timeout_min:
            remaining_min = progress_timeout_min - diff_min
            reply_text = pluralize(remaining_min, captions["countdown_past_progress"])
        else:
            reply_text = pluralize(diff_min, captions["countdown_past"])

        reply_text = reply_text.format(n=diff_min)
        bot.reply_to(message, text=reply_text, reply_markup=markup)
    elif countdown_dt > now_dt:
        diff = countdown_dt - now_dt
        diff_min = int(diff.total_seconds() / 60)
        reply_text = pluralize(diff_min, captions["countdown"], weekday=now_weekday, time_hh_mm=now_time_hh_mm)
        bot.reply_to(message, text=reply_text, reply_markup=markup)
    else:
        reply_text = captions["countdown_now"]
        reply_text = reply_text.format(weekday=now_weekday, time_hh_mm=now_time_hh_mm)
        bot.reply_to(message, text=reply_text, reply_markup=markup)


try:
    logging.info("Starting the bot...")
    logging.info("Running in %s mode", "webhook" if config["webhook"] else "polling")

    if config["webhook"]:
        logging.debug("Webhook domain: %s", WEBHOOK_DOMAIN)
        logging.debug("Webhook port: %d", WEBHOOK_PORT)
        bot.run_webhooks(
            listen="0.0.0.0", port=WEBHOOK_PORT,
            webhook_url="https://{}:{}/{}/".format(WEBHOOK_DOMAIN, WEBHOOK_PORT, BOT_TOKEN)
        )
    else:
        bot.infinity_polling()

    logging.info("Normally stopping the bot!")
except Exception as e:
    logging.critical("Uncaught exception while running the bot", exc_info=e)
    exit(1)