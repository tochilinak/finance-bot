"""Module for /cancel command."""
from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    CommandHandler
)


def cancel(update: Update, context: CallbackContext):
    """End the conversation."""
    update.message.reply_text("Okay, we can do something else")
    return ConversationHandler.END


# Create handler for /cancel command
cancel_handler = CommandHandler("cancel", cancel)
