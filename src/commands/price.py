from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler
)
from api_requests import current_cost
from commands.basic import cancel_handler
from commands.bot_filters import simple_text_filter


def price_start(update: Update, context: CallbackContext):
    """
    This callback is executed by /price.

    Give the price of the company's shares for the specified period in the end
    of conversation.

    Return key of the next part of conversation.
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
        "a period with the / periods command"
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


# Create handlers for different period types
period_type_hanlers = [
    CommandHandler("last_update", current_price),
    CommandHandler("periods", periods)
]

price_handler = ConversationHandler(
            entry_points=[CommandHandler("price", price_start)],
            states={
                "ticker": [MessageHandler(simple_text_filter, get_ticker)],
                "period_type": period_type_hanlers
            },
            fallbacks=[cancel_handler]
        )
