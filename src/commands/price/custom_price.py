from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
from api_requests import get_period_data_of_cost
from graphics import draw_plot
from commands.price.price import information_exists, PLOT_FILENAME


def custom(update: Update, context: CallbackContext):
    """Get ticker from user and ask dates for custom request."""
    ticker = context.user_data["ticker"].upper()

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
    ticker = context.user_data["ticker"]

    text = update.message.text

    try:
        start_date, end_date = text.split(' ')
    except ValueError:
        update.message.reply_text(
            "Dates entered incorrectly\n"
            "Format: YYYY-MM-DD YYYY-MM-DD\n"
            "Example: 2020-01-01 2020-11-01\n"
            "Try again or /cancel"
        )
        return "get_custom_period"

    dates, values = get_period_data_of_cost(start_date, end_date, ticker)

    if not information_exists(update, values):
        #  Ask for ticker again if price was not found
        return "ticker"

    # Draw plot in file if information exists
    draw_plot(dates, values, PLOT_FILENAME)

    img = open(PLOT_FILENAME, 'rb')

    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=img
    )

    return ConversationHandler.END
