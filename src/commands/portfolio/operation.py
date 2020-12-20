from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackContext
)
from re import match
from commands.bot_filters import OPERATION_INFO


def handle_operation(update: Update, context: CallbackContext):
    text: str = " ".join(context.args)
    if not match(OPERATION_INFO, text):
        update.message.reply_text(
            "Enter information about the operation after command\n"
            "Format: /operation_command ticker, number, date(YYYY-MM-DD)\n"
            "Example: /buy GOOGL, 7, 2017-10-13\n"
        )
        return

    ticker, number, date = text.split(", ")
    if match(r'/buy*', update.message.text):
        pass
    else:
        pass
    pass


buy_handler = CommandHandler("buy", handle_operation)
sell_handler = CommandHandler("sell", handle_operation)
