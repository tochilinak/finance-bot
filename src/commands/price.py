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
from commands.basic import cancel_handler
from commands.bot_filters import simple_text_filter


def price_start(update: Update, context: CallbackContext):
    """
    Srart of conversation.

    Asks for a ешслук if it is not specified and return key to the next part
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

    update.message.reply_text(
        "For what period are you interested in the price?"
    )
    update.message.reply_text(
        "You can get information about entering "
        "a period with the /periods command"
    )
    return "period_type"


def get_ticker(update: Update, context: CallbackContext):
    """Get company ticker from user and ask about period."""
    ticker = update.message.text
    context.user_data["ticker"] = ticker

    update.message.reply_text(
        "For what period are you interested in the price?"
    )
    update.message.reply_text(
        "You can get information about entering "
        "a period with the /periods command"
    )
    return "period_type"


def periods(update: Update, context: CallbackContext):
    """Give user information about entering a period."""
    update.message.reply_text(
        "/last_update - get the most current price available\n"
        "/custom - get prices for a specified period of time\n"
    )
    return "period_type"


def current_price(update: Update, context: CallbackContext):
    """Send the company current price to the chat with specified chat id."""
    ticker = context.user_data["ticker"]

    ticker = ticker.upper()

    price = current_cost(ticker)

    if price is not None:
        message_text = ticker + " stock price is " + str(price)
    else:
        message_text = "I don't know this price"

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=message_text
    )

    return ConversationHandler.END


def custom(update: Update, context: CallbackContext):
    ticker = context.user_data["ticker"].upper()

    update.message.reply_text(
        "Enter start and end date, format 'YYYY-MM-DD'"
    )

    return "get_custom_period"


def give_custom_price(update: Update, context: CallbackContext):
    text = update.message.text
    start_date, end_date = text.split(' ')

    ticker = context.user_data["ticker"]

    dates, values = get_period_data_of_cost(start_date, end_date, ticker)
    filename = "images/" + str(update.message.chat_id)
    svg_filename = filename + ".svg"

    draw_plot(dates, values, filename)

    img = ""  # ?????????????????????????????

    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=img
    )

    return ConversationHandler.END


# Create handlers for different period types
period_type_hanlers = [
    CommandHandler("last_update", current_price),
    CommandHandler("custom", custom),
    CommandHandler("periods", periods)
]

# Create handler for custom period
custom_period_handler = MessageHandler(simple_text_filter, give_custom_price)

price_handler = ConversationHandler(
            entry_points=[CommandHandler("price", price_start)],
            states={
                "ticker": [MessageHandler(simple_text_filter, get_ticker)],
                "period_type": period_type_hanlers,
                "get_custom_period": [custom_period_handler]
            },
            fallbacks=[cancel_handler]
        )
