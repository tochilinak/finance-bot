from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
from api_requests import get_period_data_of_cost, get_currency
from graphics import draw_multiplot, PlotData


PLOT_FILENAME = "plot.png"


def give_custom_price(update: Update, context: CallbackContext):
    """Get dates from user. Draw and send plot"""

    period = context.user_data["period"]
    start_date, end_date = period.data.split(' ')

    tickers = context.user_data["tickers"]
    list_plot_data = []
    for ticker in tickers:
        ticker = ticker.upper()
        dates, values = get_period_data_of_cost(start_date, end_date, ticker)

        if not values:
            update.message.reply_text(
                f"I have no information about {ticker}"
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

        with open(PLOT_FILENAME, 'rb') as img:
            context.bot.send_photo(
                chat_id=update.message.chat_id,
                photo=img
            )

    return ConversationHandler.END
