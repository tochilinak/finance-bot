from telegram import Update
from telegram.ext import (
    CallbackContext
)
from re import fullmatch
from datetime import datetime, timedelta
from commands.bot_filters import some_days
from commands.price.custom_price import give_custom_price


def days(update: Update, context: CallbackContext):
    """Ask number of days for request."""

    update.message.reply_text(
        "Enter number of days"
    )

    update.message.reply_text(
        "You can just enter 'n days' after the ticker message next time "
        "(and not use /days)"
    )

    return "get_number_of_days"


def give_days_price(update: Update, context: CallbackContext):
    """Get dates from user. Draw and send plot"""

    text = update.message.text

    if fullmatch(some_days, text):
        numebr_of_days = text.split(' ')[0]
    elif fullmatch(r'^\d+$', text):
        numebr_of_days = text
    else:
        update.message.reply_text(
            "Enter number of days\n"
            "Try again or /cancel"
        )
        return "get_number_of_days"

    today = datetime.now().date()
    start_date = today - timedelta(days=int(numebr_of_days))
    update.message.text = " ".join([str(start_date), str(today)])
    print(update.message.text)

    return give_custom_price(update, context)
