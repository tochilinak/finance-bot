"""Module for /cancel command and unknow actions."""
from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    CommandHandler,
    MessageHandler
)
from commands.bot_filters import command_filter


def cancel(update: Update, context: CallbackContext):
    """End the conversation."""
    update.message.reply_text("Okay, we can do something else")
    return ConversationHandler.END


def unknown_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "I don't know this command"
    )
    update.message.reply_text(
        "Or you can't use it now"
    )


# Create handler for /cancel command
cancel_handler = CommandHandler("cancel", cancel)

# Create handler for unknown commands
unknown_handler = MessageHandler(command_filter, unknown_command)
