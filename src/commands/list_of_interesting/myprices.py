from telegram import Update, ParseMode
from telegram.ext import (
    CommandHandler,
    CallbackContext
)
from database import list_users_tickers
from api_requests import current_cost


def info_line(ticker: str):
    """Cretate string in format "ticker: price"."""
    price = current_cost(ticker)
    price = str(price).replace(".", r"\.") if price else "no information"
    return "*%s:* %s" % (ticker, price)


def myprices(update: Update, context: CallbackContext):
    """Action for /myprices command."""
    chat_id = update.message.chat_id
    tickers = list_users_tickers(chat_id)
    text = "\n".join([info_line(ticker) for ticker in tickers])
    context.bot.send_message(
        text=text,
        chat_id=chat_id,
        parse_mode=ParseMode.MARKDOWN_V2
    )


myprices_handler = CommandHandler("myprices", myprices)
