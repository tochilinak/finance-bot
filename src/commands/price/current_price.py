from telegram import Update, ParseMode
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
from api_requests import async_request, QueryType
from queries.general import QueryData


def info_line(query_data: QueryData):
    """Cretate string in format "ticker: price"."""
    ticker = query_data.symbol
    cost = query_data.result[QueryType.CURRENT_COST]
    currency = query_data.result[QueryType.CURRENCY]
    last_update = None

    if not cost or not currency:
        price = "no information"
        currency = ""
    else:
        price, last_update = cost
        price = str(price).replace(".", r"\.")
        last_update = last_update.replace("-", r"\-")

    result = r"*%s:* %s %s" % (ticker, price, currency)
    if last_update:
        result += r" \(last updated: %s\)" % (last_update)

    return result


def get_results(tickers):
    query_data_list = [QueryData(symbol=x.upper()) for x in tickers]
    async_request(query_data_list, [QueryType.CURRENT_COST,
                                    QueryType.CURRENCY])
    return query_data_list


def current_price(update: Update, context: CallbackContext):
    """Send the companies current prices to the chat with specified chat id."""
    tickers = context.user_data["tickers"]

    if tickers:
        results = get_results(tickers)
        text = "\n".join([info_line(res) for res in results])
    else:
        text = "Your list of companies of interest is empty"

    context.bot.send_message(
        text=text,
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN_V2
    )

    return ConversationHandler.END
