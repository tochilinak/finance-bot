from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackContext
)
from database import get_list_of_operations


CSV_FILENAME = "out.csv"


def give_list(update: Update, context: CallbackContext):
    """Reaction to /operation_list."""
    chat_id = update.message.chat_id
    get_list_of_operations(chat_id)

    with open(CSV_FILENAME, 'rb') as file:
        context.bot.send_document(
            document=file,
            chat_id=chat_id
        )


operation_list_handler = CommandHandler("operation_list", give_list)
