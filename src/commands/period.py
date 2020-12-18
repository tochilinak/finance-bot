from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    CommandHandler,
    MessageHandler
)
from re import match
from datetime import datetime, timedelta
from commands.basic import default_fallbacks
from commands.bot_filters import (se_dates, some_days, se_dates_filter,
                                  some_days_filter, simple_text_filter)


class Period:
    """Classs for information about period entered by user."""

    def __init__(self, period_type, data=None):
        self.period_type = period_type
        self.data = data


def create_custom_period(context: CallbackContext, text: str):
    if match(se_dates, text):
        context.user_data["period"] = Period("cd", text)
        return True
    return False


def create_some_days_period(context: CallbackContext, text: str):
    if match(some_days, text):
        numebr_of_days = text.split(' ')[0]
        today = datetime.now().date()
        start_date = today - timedelta(days=int(numebr_of_days))
        text = " ".join([str(start_date), str(today)])
        context.user_data["period"] = Period("cd", text)
        return True
    return False


def is_number(text: str):
    if match(r"\d+$", text):
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
    text = update.message.text
    if text is None:
        return ask_period(update)
    else:
        if create_custom_period(context, text):
            return "got_period"
        if create_some_days_period(context, text):
            return "got_period"
        return ask_period(update)


def periods(update: Update, context: CallbackContext):
    """Give user information about entering a period."""
    update.message.reply_text(
        "/last_update - get the most current prices available\n"
        "/custom - get prices for a specified period of time\n"
        "/days - get price for last n days\n"
    )
    return "period"


def last_update(update: Update, context: CallbackContext):
    """Reaction to /last_update."""
    context.user_data["period"] = Period("lu")
    return "got_period"


def custom(update: Update, context: CallbackContext):
    """Reaction to /custom. Ask dates for custom request."""

    update.message.reply_text(
        "Enter start and end date, format 'YYYY-MM-DD YYYY-MM-DD'"
    )

    update.message.reply_text(
        "You can just enter two dates after the ticker message next time "
        "(and not use /custom)"
    )

    return "get_custom_period"


def get_custom_period(update: Update, context: CallbackContext):
    text = update.message.text
    if create_custom_period(context, text):
        return "got_period"

    update.message.reply_text(
        "Try again, format 'YYYY-MM-DD YYYY-MM-DD'"
    )
    return "get_custom_period"


def days(update: Update, context: CallbackContext):
    """Reaction to /days. Ask number of days for request."""

    update.message.reply_text(
        "Enter number of days"
    )

    update.message.reply_text(
        "You can just enter 'n days' after the ticker message next time "
        "(and not use /days)"
    )

    return "get_number_of_days"


def get_number_of_days(update: Update, context: CallbackContext):
    text = update.message.text
    if create_some_days_period(context, text):
        return "got_period"
    if is_number(text):
        create_some_days_period(context, text + " days")
        return "got_period"

    update.message.reply_text(
        "Try again, enter number of days"
    )
    return "get_number_of_days"


independent_handlers = [
    CommandHandler("days", days),
    CommandHandler("custom", custom),
    CommandHandler("last_update", last_update),
    MessageHandler(some_days_filter, get_number_of_days),
    MessageHandler(se_dates_filter, get_custom_period)
]

get_period_handler = ConversationHandler(
    entry_points=independent_handlers,
    states={"period": [
        *independent_handlers, CommandHandler("periods", periods)],
            "get_custom_period": [
                MessageHandler(simple_text_filter, get_custom_period)],
            "get_number_of_days": [
                MessageHandler(simple_text_filter, get_number_of_days)
            ]
    },
    fallbacks=default_fallbacks,
    map_to_parent={"got_period": "got_period",
                   ConversationHandler.END: ConversationHandler.END}
)
