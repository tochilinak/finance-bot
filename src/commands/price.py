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
from api_requests import current_cost, get_period_data_of_cost
from graphics import draw_plot
from commands.basic import default_fallbacks
from commands.bot_filters import simple_text_filter, se_dates_filter

PLOT_FILENAME = "images/plot.png"


def ask_period(update: Update):
    """Send some messages."""
    update.message.reply_text(
        "For what period are you interested in the price?"
    )
    update.message.reply_text(
        "You can get information about entering "
        "a period with the /periods command"
    )
    return "period"


def information_exists(update: Update, data):
    """Check if any information is written in the data."""
    if data is None:
        update.message.reply_text(
            "I don't have this information\n"
            "You may have entered the wrong ticker\n"
            "Try again or /cancel"
        )
        return False

    return True


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
            "Enter a company ticker "
        )
        return "ticker"

    ticker = ' '.join(context.args)
    context.user_data["ticker"] = ticker

    return ask_period(update)


def get_ticker(update: Update, context: CallbackContext):
    """Get company ticker from user and ask about period."""
    ticker = update.message.text
    context.user_data["ticker"] = ticker

    return ask_period(update)


def periods(update: Update, context: CallbackContext):
    """Give user information about entering a period."""
    update.message.reply_text(
        "/last_update - get the most current price available\n"
        "/custom - get prices for a specified period of time\n"
    )
    return "period"


def current_price(update: Update, context: CallbackContext):
    """Send the company current price to the chat with specified chat id."""
    ticker = context.user_data["ticker"]

    ticker = ticker.upper()

    price = current_cost(ticker)

    if not information_exists(update, price):
        #  Ask for ticker again if price was not found
        return "ticker"

    message_text = ticker + " stock price is " + str(price)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=message_text
    )

    return ConversationHandler.END


def custom(update: Update, context: CallbackContext):
    """Get ticker from user and ask dates for custom request."""
    ticker = context.user_data["ticker"].upper()

    update.message.reply_text(
        "Enter start and end date, format 'YYYY-MM-DD YYYY-MM-DD'"
    )

    update.message.reply_text(
        "You can just enter two dates after the ticker message next time "
        "(and not use /custom)"
    )

    return "get_custom_period"


def give_custom_price(update: Update, context: CallbackContext):
    """Get dates from user. Draw and send plot"""
    ticker = context.user_data["ticker"]

    text = update.message.text

    try:
        start_date, end_date = text.split(' ')
    except ValueError:
        update.message.reply_text(
            "Dates entered incorrectly\n"
            "Format: YYYY-MM-DD YYYY-MM-DD\n"
            "Example: 2020-01-01 2020-11-01\n"
            "Try again or /cancel"
        )
        return "get_custom_period"

    dates, values = get_period_data_of_cost(start_date, end_date, ticker)

    if not information_exists(update, values):
        #  Ask for ticker again if price was not found
        return "ticker"

    # Draw plot in file if information exists
    draw_plot(dates, values, PLOT_FILENAME)

    img = open(PLOT_FILENAME, 'rb')

    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=img
    )

    return ConversationHandler.END


# Create handlers for custom period
custom_period_handler = MessageHandler(se_dates_filter, give_custom_price)
get_custom_period_handler = MessageHandler(
    simple_text_filter,
    give_custom_price
)

# Create handlers for different periods
period_hanlers = [
    CommandHandler("last_update", current_price),
    CommandHandler("custom", custom),
    CommandHandler("periods", periods),
    custom_period_handler
]


price_handler = ConversationHandler(
    entry_points=[CommandHandler("price", price_start)],
    states={
        "ticker": [MessageHandler(simple_text_filter, get_ticker)],
        "period": period_hanlers,
        "get_custom_period": [get_custom_period_handler]
    },
    fallbacks=default_fallbacks
)
