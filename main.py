import logging
from os import environ

from dotenv import load_dotenv
import telebot

from countdown import CountdownData, get_countdown_message
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


start_markup = telebot.util.quick_markup({
    captions["start"]["button"]: {'callback_data': 'start_button'},
    captions["start"]["github"]["caption"]: {'url': captions["start"]["github"]["url"]}
}, row_width=1)

choose_format_markup = telebot.util.quick_markup({
    captions["choose_format"]["days"]: {'callback_data': 'choose_format_days'},
    captions["choose_format"]["hours"]: {'callback_data': 'choose_format_hours'},
    captions["choose_format"]["minutes"]: {'callback_data': 'choose_format_minutes'},
    captions["home"]: {'callback_data': 'home'}
})


def get_countdown_markup(format: str) -> telebot.types.InlineKeyboardMarkup:
    countdown_markup = telebot.util.quick_markup({
        captions["countdown"]["refresh"]: {'callback_data': f'refresh_{format}'},
        captions["home"]: {'callback_data': 'home'}
    })

    return countdown_markup


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, captions["start"]["message"], reply_markup=start_markup)


@bot.callback_query_handler(func=lambda m: m.data == "start_button")
def start_button_call_handler(call):
    bot.edit_message_text(captions["choose_format"]["message"], call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=choose_format_markup)


@bot.callback_query_handler(func=lambda m: m.data == "home")
def home_call_handler(call):
    bot.edit_message_text(captions["start"]["message"], call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=start_markup)


@bot.callback_query_handler(func=lambda m: m.data.startswith("choose_format_"))
def choose_format_call_handler(call):
    required_format = call.data.replace("choose_format_", "")
    markup = get_countdown_markup(required_format)
    message = get_countdown_message(cd=CountdownData(weekday_captions=captions["countdown"]["weekday"], data=data), countdown_captions=captions["countdown"], format=required_format)

    bot.edit_message_text(message, call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda m: m.data.startswith("refresh_"))
def refresh_call_handler(call):
    call.data = call.data.replace("refresh_", "")
    return choose_format_call_handler(call)


try:
    logging.info("Starting the bot...")
    logging.info("Running in %s mode", "webhook" if config["webhook"] else "polling")
    logging.info("Calling deleteWebhook, to avoid getUpdates method error, when webhook is active")
    bot.delete_webhook()

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