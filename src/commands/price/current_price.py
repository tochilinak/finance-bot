from telegram import Update, ParseMode
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
from api_requests import current_cost, get_currency


def info_line(ticker: str):
    """Cretate string in format "ticker: price"."""
    ticker = ticker.upper()
    result = current_cost(ticker)
    currency = get_currency(ticker)

    if not result or not currency:
        price = "no information"
        currency = ""
    else:
        price, last_update = result
        price = str(price).replace(".", r"\.")
        last_update = last_update.replace("-", r"\-")

    return r"*%s:* %s %s \(last updated: %s\)" % (ticker, price, currency,
                                               last_update)


def current_price(update: Update, context: CallbackContext):
    """Send the companies current prices to the chat with specified chat id."""
    tickers = context.user_data["tickers"]

    if tickers:
        text = "\n".join([info_line(ticker) for ticker in tickers])
    else:
        text = "Your list of companies of interest is empty"

    context.bot.send_message(
        text=text,
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN_V2
    )

    return ConversationHandler.END
