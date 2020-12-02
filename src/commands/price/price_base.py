from telegram import Update


def information_exists(update: Update, data):
    """Check if any information is written in the data."""
    if data is None:
        update.message.reply_text(
            "I don't have this information\n"
            "You may have entered the wrong ticker\n"
            "Try again or /cancel"
        )
        return False

    return True


PLOT_FILENAME = "images/plot.png"
