from telegram import Update, ParseMode
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
from api_requests import current_cost, get_currency


def info_line(ticker: str):
    """Cretate string in format "ticker: price"."""
    ticker = ticker.upper()
    price = current_cost(ticker)
    currency = get_currency(ticker)

    if not price or not currency:
        price = "no information"
        currency = ""
    else:
        price = str(price).replace(".", r"\.")

    return "*%s:* %s %s" % (ticker, price, currency)


def current_price(update: Update, context: CallbackContext):
    """Send the company current price to the chat with specified chat id."""
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
