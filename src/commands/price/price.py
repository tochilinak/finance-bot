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
from commands.basic import default_fallbacks
from commands.bot_filters import (simple_text_filter,
                                  se_dates_filter,
                                  some_days_filter
                                  )
from commands.price.current_price import current_price
from commands.price.custom_price import custom, give_custom_price
from commands.price.days import days, give_days_price


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


def get_ticker(update: Update, context: CallbackContext):
    """Get company ticker or "my" from user and ask about period."""
    text = update.message.text
    if text == "my":
        context.user_data["tickers"] = tickers_list(update.message.chat_id)
    else:
        context.user_data["tickers"] = [text.upper()]

    return ask_period(update)


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
            "Enter a company ticker or 'my' for prices from your list of"
            "companies of interest"
        )
        return "ticker"

    update.message.text = ' '.join(context.args)
    return get_ticker(update, context)


def periods(update: Update, context: CallbackContext):
    """Give user information about entering a period."""
    update.message.reply_text(
        "/last_update - get the most current prices available\n"
        "/custom - get prices for a specified period of time\n"
        "/days - get price for last n days\n"
    )
    return "period"


# Create handlers for custom period
# This reacts on message with 2 dates after message with ticker
custom_period_handler = MessageHandler(se_dates_filter, give_custom_price)
# This reacts on text message after command /custom
get_custom_period_handler = MessageHandler(
    simple_text_filter,
    give_custom_price
)

# Create handlers for periods in format 'n days'
# This reacts on message in format 'n days' after message with ticker
days_handler = MessageHandler(some_days_filter, give_days_price)
# This reacts on text message after command /days
get_days_handler = MessageHandler(
    simple_text_filter,
    give_days_price
)

# Create handlers for different periods
period_hanlers = [
    # give user information about perid entering after /periods command
    CommandHandler("periods", periods),

    # give user last price after /last_update command
    CommandHandler("last_update", current_price),

    # ask user for 2 dates after /custom command
    CommandHandler("custom", custom),
    # give user price in specified period
    custom_period_handler,

    # ask user for number of days after /days command
    CommandHandler("days", days),
    # give user price in last n days
    days_handler
]

price_handler = ConversationHandler(
    entry_points=[CommandHandler("price", price_start)],
    states={
        "ticker": [MessageHandler(simple_text_filter, get_ticker)],
        "period": period_hanlers,
        "get_custom_period": [get_custom_period_handler],
        "get_number_of_days": [get_days_handler]
    },
    fallbacks=default_fallbacks
)
