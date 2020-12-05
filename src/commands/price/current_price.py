from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
from api_requests import current_cost, get_currency
from commands.price.price_base import information_exists


def current_price(update: Update, context: CallbackContext):
    """Send the company current price to the chat with specified chat id."""
    ticker = context.user_data["ticker"]

    ticker = ticker.upper()

    price = current_cost(ticker)

    if not information_exists(update, price):
        #  Ask for ticker again if price was not found
        return "ticker"

    currency = get_currency(ticker)
    message_text = "%s stock price is %s %s" % (ticker, str(price), currency)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=message_text
    )

    return ConversationHandler.END
