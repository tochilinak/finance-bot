"""Module for /cancel command and unknow actions."""
from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    CommandHandler,
    MessageHandler
)
from commands.bot_filters import command_filter, simple_text_filter


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


def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text(
        "I don't understand you"
    )


# Create handler for /cancel command
cancel_handler = CommandHandler("cancel", cancel)

# Create handler for unknown commands
unknown_command_handler = MessageHandler(command_filter, unknown_command)

# Create handler for unknown text
unknown_text_handler = MessageHandler(simple_text_filter, unknown_text)

# Create fallbacks for conversation
default_fallbacks = [
    cancel_handler,
    unknown_command_handler,
    unknown_text_handler
]
