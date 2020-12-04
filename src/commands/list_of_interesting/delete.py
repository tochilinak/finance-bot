from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler
)
from commands.basic import simple_text_filter, default_fallbacks


def delete(update: Update, context: CallbackContext):
    ticker = update.message.text
    chat_id = update.message.chat_id
    # delete company from db
    update.message.reply_text("Deleted succefully!")
    return ConversationHandler.END


def delete_start(update: Update, context: CallbackContext):
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

    ticker = ' '.join(context.args)
    update.message.text = ticker
    return delete(update, context)


delete_from_list_handler = ConversationHandler(
    entry_points=[CommandHandler("delete", delete_start)],
    states={"ticker": [MessageHandler(simple_text_filter, delete)]},
    fallbacks=default_fallbacks
)
