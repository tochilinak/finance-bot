from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler
)
from commands.basic import simple_text_filter, default_fallbacks
from database import add_users_ticker


def add(update: Update, context: CallbackContext):
    """Add ticker from messege to user's list and finish conversation."""
    ticker = update.message.text.upper()
    chat_id = update.message.chat_id
    add_users_ticker(chat_id, ticker)
    update.message.reply_text("Added %s succefully!" % ticker)
    return ConversationHandler.END


def add_start(update: Update, context: CallbackContext):
    """
    Start of conversation.

    If text after "/add" exists add this ticker to list if interesting
    Else ask for ticker
    """
    # context.args is list of words after command
    if not context.args:
        update.message.reply_text(
            'You can use the command like this: "/add <company ticker>"'
        )
        update.message.reply_text(
            "Ok, now I need to know the company you are interested in\n"
            "Enter a company ticker "
        )
        return "ticker"

    # delete "/add" from message text
    ticker = ' '.join(context.args)
    update.message.text = ticker
    return add(update, context)


add_to_list_handler = ConversationHandler(
    entry_points=[CommandHandler("add", add_start)],
    states={"ticker": [MessageHandler(simple_text_filter, add)]},
    fallbacks=default_fallbacks
)
