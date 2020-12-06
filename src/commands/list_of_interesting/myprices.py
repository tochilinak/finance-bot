from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackContext
)
from database import list_users_tickers


def myprices(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = list_users_tickers(chat_id)
    update.message.reply_text(text)


myprices_handler = CommandHandler("myprices", myprices)
