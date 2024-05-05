from datetime import datetime, timedelta
import logging
from os import environ

from dotenv import load_dotenv
import telebot

from pluralize import pluralize
from read_json import ReadJSONException, read_json

load_dotenv()
BOT_TOKEN = environ.get("BOT_TOKEN") or ""
LOG_LEVEL = int(environ.get("LOG_LEVEL")) or 20

logging.basicConfig(level=LOG_LEVEL)
logging.debug("Bot token: %s", BOT_TOKEN)
logging.debug("Log level: %d", LOG_LEVEL)


try:
    logging.info("Reading data...")
    data = read_json("data.json")
    captions = read_json("captions.json")
    logging.info("Done reading data!")
except ReadJSONException as e:
    logging.error("Error while reading data and captions", exc_info=e)
    exit(1)
except Exception as e:
    logging.critical("Uncaught exception while reading data and captions", exc_info=e)
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

        if diff_min < progress_timeout_min:
            reply_text = pluralize(diff_min, captions["countdown_past_progress"])
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
    bot.infinity_polling()
    logging.info("Normally stopping the bot!")
except Exception as e:
    logging.critical("Uncaught exception while running the bot", exc_info=e)
    exit(1)