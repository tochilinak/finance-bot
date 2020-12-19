"""
Create handler for /price command.

Command give user prices for the company's shares for the specified period
User can enter "/price <company ticker>" or just "/price"
"""
from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler
)
from database import list_users_tickers as tickers_list
from commands.basic import default_fallbacks, default_map_to_parent
from commands.bot_filters import simple_text_filter
from commands.price.current_price import current_price
from commands.price.custom_price import give_custom_price
from commands.period import PeriodGetter


def give_price(update: Update, context: CallbackContext):
    period = context.user_data["period"]
    if period.period_type == "lu":
        return current_price(update, context)
    if period.period_type == "cd":
        return give_custom_price(update, context)
    return ConversationHandler.END


PERIOD_GETTER = PeriodGetter(give_price, default_map_to_parent)


def price_start(update: Update, context: CallbackContext):
    """
    Srart of conversation.

    Asks for a ticker if it is not specified and return key to the next part
    of conversation.
    """
    # context.args is list of words after command
    if not context.args:
        update.message.reply_text(
            'You can use the command like this: "/price <company ticker>"'
        )
        update.message.reply_text(
            "Ok, now I need to know the company you are interested in\n"
            "Enter a company ticker or 'my' for prices from your list of "
            "companies of interest"
        )
        return "ticker"

    # /price is useless part of message now
    update.message.text = ' '.join(context.args)
    return get_ticker(update, context)


def get_ticker(update: Update, context: CallbackContext):
    """
    Get company ticker or "my" from user and ask about period.

    It can be activated from pricestart (ticker specified) or at state "ticker"
    """
    text = update.message.text.upper()
    if text == "MY":
        context.user_data["tickers"] = tickers_list(update.message.chat_id)
    else:
        context.user_data["tickers"] = [text.upper()]

    # ticker is useless part of message now
    update.message.text = ''
    return PERIOD_GETTER.start_getting_period()(update, context)


price_handler = ConversationHandler(
    entry_points=[CommandHandler("price", price_start)],
    states={
        "ticker": [MessageHandler(simple_text_filter, get_ticker)],
        "period": [PERIOD_GETTER.get_period_handler()]
    },
    fallbacks=default_fallbacks
)
