from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
from re import fullmatch
from api_requests import get_period_data_of_cost, get_currency
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


def give_custom_price(update: Update, context: CallbackContext):
    """Get dates from user. Draw and send plot"""

    text = update.message.text

    if fullmatch(r'^\d{4}-\d{2}-\d{2} \d{4}-\d{2}-\d{2}$', text):
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
    for ticker in tickers:
        ticker = ticker.upper()
        dates, values = get_period_data_of_cost(start_date, end_date, ticker)

        if not values:
            update.message.reply_text(
                f"I have not information about {ticker}"
            )
        else:
            currency = get_currency(ticker)
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
