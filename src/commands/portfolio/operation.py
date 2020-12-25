from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackContext
)
from re import match
from commands.bot_filters import OPERATION_INFO, PRICE_OPERATION_INFO
from database import OperationType as OpT, add_operation


def handle_operation(update: Update, context: CallbackContext):
    """Reaction to /buy or /sell."""
    text: str = " ".join(context.args)
    if not (match(OPERATION_INFO, text) or match(PRICE_OPERATION_INFO, text)):
        update.message.reply_text(
            "Enter information about the operation after command\n"
            "Format: /operation_command ticker, number, date(YYYY-MM-DD), "
            "price(optional)\n"
            "Examples:\n"
            "/buy GOOGL, 7, 2017-10-13\n"
            "/sell yndx, 3, 2020-12-23, 5023\n"
        )
        return

    c_id = update.message.chat_id
    args = text.split(", ")
    if match(r'/buy*', update.message.text):
        res = add_operation(c_id, OpT.BUY, *args)
    else:
        res = add_operation(c_id, OpT.SELL, *args)
    if res:
        update.message.reply_text("Added operation successfully")
    else:
        update.message.reply_text("The date may be incorrect")


buy_handler = CommandHandler("buy", handle_operation)
sell_handler = CommandHandler("sell", handle_operation)
