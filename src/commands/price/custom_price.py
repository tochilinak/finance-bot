from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
from re import fullmatch
from commands.bot_filters import se_dates
from api_requests import async_request, QueryType
from queries.general import QueryData
from graphics import draw_multiplot, PlotData
from commands.price.price_base import PLOT_FILENAME


def custom(update: Update, context: CallbackContext):
    """Ask dates for custom request."""

    update.message.reply_text(
        "Enter start and end date, format 'YYYY-MM-DD YYYY-MM-DD'"
    )

    update.message.reply_text(
        "You can just enter two dates after the ticker message next time "
        "(and not use /custom)"
    )

    return "get_custom_period"


def get_results(tickers, start_date, end_date):
    query_data_list = [QueryData(symbol=x.upper(), start_date = start_date,
                       end_date=end_date) for x in tickers]
    async_request(query_data_list, [QueryType.PERIOD_COST, QueryType.CURRENCY])
    return query_data_list


def give_custom_price(update: Update, context: CallbackContext):
    """Get dates from user. Draw and send plot"""

    text = update.message.text

    if fullmatch(se_dates, text):
        start_date, end_date = text.split(' ')
    else:
        update.message.reply_text(
            "Dates entered incorrectly\n"
            "Format: YYYY-MM-DD YYYY-MM-DD\n"
            "Example: 2020-01-01 2020-11-01\n"
            "Try again or /cancel"
        )
        return "get_custom_period"

    tickers = context.user_data["tickers"]
    list_plot_data = []
    results = get_results(tickers, start_date, end_date)
    for query_data in results:
        ticker = query_data.symbol
        dates, values = query_data.result[QueryType.PERIOD_COST]

        if not values:
            update.message.reply_text(
                f"I have no information about {ticker}"
            )
        else:
            currency = query_data.result[QueryType.CURRENCY]
            title = f"{ticker} stock price"
            plot_data = PlotData(dates, values, title, currency)
            list_plot_data.append(plot_data)

    # Draw plot in file if information exists
    if list_plot_data:
        draw_multiplot(list_plot_data,
                       PLOT_FILENAME,
                       title=f"Prices from {start_date} to {end_date}"
                       )

        img = open(PLOT_FILENAME, 'rb')

        context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=img
        )

    return ConversationHandler.END
