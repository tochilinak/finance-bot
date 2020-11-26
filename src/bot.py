from typing import Optional

from telegram import Update, ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext, Filters,
    ConversationHandler,
    MessageHandler
)
import config
from api_requests import current_cost, symbol_by_name


def start(update: Update, context: CallbackContext):
    """Send starting message to user whose message generated this update."""
    update.message.reply_text("Hello\n" "I am finance bot")
    update.message.reply_text("You can always get list of commands with /help")
    help_bot(update, context)


def help_bot(update: Update, context: CallbackContext):
    """Send info message to the user whose message generated this update."""
    update.message.reply_text("This is list of available commands:")
    update.message.reply_text(
        "/start - start me\n"

        "/help - get some information\n"

        "/price - get company stock price\n"

        "/find_company - find company by name. Use it if you want to know "
        "company ticker\n"
    )


def cancel(update: Update, context: CallbackContext):
    """End the conversation."""
    update.message.reply_text("Okay, we can do something else")
    return ConversationHandler.END


def price_start(update: Update, context: CallbackContext):
    """
    Ask user about company ticker. This callback is executed by /price.

    Return key of next part of conversation
    """
    update.message.reply_text(
        "Ok, now I need to know the company you are interested in\n"
        "Enter a company ticker "
    )
    update.message.reply_text("You can stop with /cancel")
    return "company"


def get_company(update: Update, context: CallbackContext):
    """
    Get company ticker from user and start task.

    This task will tell the user company stock price.
    In the end, stop the conversation
    """
    text = update.message.text
    context.job_queue.run_once(
        callback=give_price,
        when=0,
        context={'chat_id': update.message.chat.id, "company": text}
    )
    return ConversationHandler.END


def give_price(context: CallbackContext):
    """Send the company price to the chat with specified chat id."""
    job_context: Optional[dict] = context.job.context
    company = job_context["company"]
    chat_id = job_context["chat_id"]
    company = company.upper()
    price = current_cost(company)
    if price is not None:
        message_text = company + " stock price is " + str(price)
    else:
        message_text = "I don't know this price"
    context.bot.send_message(
        chat_id=chat_id,
        text=message_text
    )


def find_company(update: Update, context: CallbackContext):
    """
    Find companies by name.

    Return list of companies (with tickers) with this name
    Asks for a name if not specified
    """

    # context.args is list of words after command
    if not context.args:
        update.message.reply_text(
            'You can use the command like this: "/find_company <company name>'
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

    # get information about id and name
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


def main():
    # Create updater and dispather for bot
    updater = Updater(token=config.TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Create filter for MessageHandler
    simple_text_filter = Filters.text & ~Filters.command

    # Add handler for /start command
    dispatcher.add_handler(CommandHandler("start", start))

    # Add handler for /help command
    dispatcher.add_handler(CommandHandler("help", help_bot))

    # Create handler for /cancel command
    cancel_handler = CommandHandler("cancel", cancel)

    # Add conversation handler for /price command
    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("price", price_start)],
            states={
                "company": [MessageHandler(simple_text_filter, get_company)],
            },
            fallbacks=[cancel_handler]
        )
    )

    # Add conversation handler for /find_company command
    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("find_company", find_company)],
            states={
                "name": [MessageHandler(simple_text_filter, get_name)],
            },
            fallbacks=[cancel_handler]
        )
    )

    # Start the bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
