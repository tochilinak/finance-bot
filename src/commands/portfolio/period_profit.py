from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
from graphics import draw_multiplot, PlotData
from database import get_period_profit

PLOT_FILENAME = "plot.png"


def period_profit(update: Update, context: CallbackContext):
    """Send plots profits(date) to the chat."""
    period = context.user_data["period"]
    start_date, end_date = period.data.split(' ')
    chat_id = update.message.chat_id

    info = get_period_profit(start_date, end_date, chat_id)
    if info:
        list_plot_data = [
            PlotData(
                dates=info[currency][0],
                y_values=info[currency][1],
                title=f"Profit for stocks in {currency}",
                ylabel="profit"

            ) for currency in info.keys()
        ]

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
