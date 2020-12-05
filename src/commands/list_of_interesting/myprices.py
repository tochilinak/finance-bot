from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackContext
)


def myprices(update: Update, context: CallbackContext):
    text = ""
    # fill text
    update.message.reply_text(text)


myprices_handler = CommandHandler("myprices", myprices)
