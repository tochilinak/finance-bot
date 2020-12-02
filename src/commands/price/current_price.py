from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
from api_requests import current_cost
from commands.price.price import information_exists


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
