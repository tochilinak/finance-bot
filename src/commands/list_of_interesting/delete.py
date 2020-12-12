from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler
)
from commands.basic import simple_text_filter, default_fallbacks
from database import delete_users_ticker


def delete(update: Update, context: CallbackContext):
    """Delete ticker from messege from user's list and finish conversation."""
    ticker = update.message.text.upper()
    chat_id = update.message.chat_id
    delete_users_ticker(chat_id, ticker)
    update.message.reply_text("Deleted succefully!")
    return ConversationHandler.END


def delete_start(update: Update, context: CallbackContext):
    """
    Start of conversation.

    If text after "/delete" exists delete this ticker from list if interesting
    Else ask for ticker
    """
    # context.args is list of words after command
    if not context.args:
        update.message.reply_text(
            'You can use the command like this: "/delete <company ticker>"'
        )
        update.message.reply_text(
            "Ok, now I need to know the company you want to delete\n"
            "Enter a company ticker "
        )
        return "ticker"

    # delete "/delete" from message text
    ticker = ' '.join(context.args)
    update.message.text = ticker
    return delete(update, context)


delete_from_list_handler = ConversationHandler(
    entry_points=[CommandHandler("delete", delete_start)],
    states={"ticker": [MessageHandler(simple_text_filter, delete)]},
    fallbacks=default_fallbacks
)
