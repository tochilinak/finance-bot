from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler
)
from commands.basic import simple_text_filter, default_fallbacks
from database import delete_operation


def delete(update: Update, context: CallbackContext):
    """Delete operation."""
    try:
        operation = int(update.message.text)
        delete_operation(operation)
        update.message.reply_text("Deleted succefully!")
    except:
        update.message.reply_text("Deleted unsuccefully!")
    return ConversationHandler.END


def delete_start(update: Update, context: CallbackContext):
    """
    Start of conversation.
    """
    # context.args is list of words after command
    if not context.args:
        update.message.reply_text(
            'You can use the command like this: "/delete_operation <id>"'
        )
        update.message.reply_text(
            "Ok, now I need to know the operation you want to delete\n"
            "Enter an operation id"
        )
        return "id"

    # delete "/delete_operation" from message text
    operation = ' '.join(context.args)
    update.message.text = operation
    return delete(update, context)


delete_operation_handler = ConversationHandler(
    entry_points=[CommandHandler("delete_operation", delete_start)],
    states={"id": [MessageHandler(simple_text_filter, delete)]},
    fallbacks=default_fallbacks
)
