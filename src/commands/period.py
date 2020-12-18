from telegram import Update
from telegram.ext import (
    CallbackContext
)
from re import match
from commands.bot_filters import se_dates, some_days


class Period:
    """Classs for information about period entered by user."""

    def __init__(self, period_type, data):
        self.period_type = period_type
        self.data = data


def is_custom_date(text: str):
    if match(se_dates, text):
        return True
    return False


def is_some_days(text: str):
    if match(some_days, text):
        return True
    return False


def ask_period(update: Update):
    """Ask about period (send some messages)."""
    update.message.reply_text(
        "For what period are you interested in the price?"
    )
    update.message.reply_text(
        "You can get information about entering "
        "a period with the /periods command"
    )
    return "period"


def start_getting(update: Update, context: CallbackContext):
    if update.message.text is None:
        return ask_period(update)
    else:
        pass
