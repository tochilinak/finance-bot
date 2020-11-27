"""
Create handler for /find_company command.

Command give user list of commands and their tickers with this name
User can enter "/find_company <company name>" or just "/find_company"
"""
from typing import Optional

from telegram import Update, ParseMode
from telegram.ext import (
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler
)
from api_requests import symbol_by_name
from commands.basic import cancel_handler
from commands.bot_filters import simple_text_filter


def find_company(update: Update, context: CallbackContext):
    """
    Srart of conversation.

    Asks for a name if it is not specified and return key to the next part
    of conversation.
    """
    # context.args is list of words after command
    if not context.args:
        update.message.reply_text(
            'You can use the command like this: "/find_company <company name>"'
        )
        update.message.reply_text(
            "Ok, now I need to know the company you are interested in\n"
            "Enter a company name "
        )
        return "name"

    name = ' '.join(context.args)

    # Start task.
    # This task will give the user list of companies and their tickers.
    context.job_queue.run_once(
        callback=give_tickers,
        when=0,
        context={"chat_id": update.message.chat.id, "name": name}
    )
    return ConversationHandler.END


def get_name(update: Update, context: CallbackContext):
    """
    Get company name from user and start task.

    This task will give the user list of companies and their tickers.
    In the end, stop the conversation
    """
    text = update.message.text
    context.job_queue.run_once(
        callback=give_tickers,
        when=0,
        context={"chat_id": update.message.chat.id, "name": text}
    )
    return ConversationHandler.END


def give_tickers(context: CallbackContext):
    """Send companies list to the chat with specified chat id."""

    def create_info_line(name: str, ticker: str) -> str:
        """Create output line for markdown using company name and ticker."""
        for symbol in {"(", ")", "-", "."}:
            name = name.replace('%s' % symbol, r'\%s' % symbol)
            ticker = ticker.replace('%s' % symbol, r'\%s' % symbol)
        res = "%s:\n*%s*" % (name, ticker)
        return res

    # get information about chat id and name
    job_context: Optional[dict] = context.job.context
    name = job_context["name"]
    chat_id = job_context["chat_id"]

    companies = symbol_by_name(name)

    if not companies:
        context.bot.send_message(
            chat_id=chat_id,
            text="I have not found a company with that name :("
        )
        return

    # "c" is "company"
    text = "\n\n".join([create_info_line(c[0], c[1]) for c in companies])

    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN_V2
    )


find_company_handler = ConversationHandler(
    entry_points=[CommandHandler("find_company", find_company)],
    states={
        "name": [MessageHandler(simple_text_filter, get_name)],
    },
    fallbacks=[cancel_handler]
)
