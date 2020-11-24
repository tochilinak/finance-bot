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
    job_context = context.job.context
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
    """

    def create_inf_line(name: str, ticker: str) -> str:
        """Create output line for markdown using company name and ticker."""
        for symbol in {"(", ")", "-", "."}:
            name = name.replace('%s' % symbol, r'\%s' % symbol)
            ticker = ticker.replace('%s' % symbol, r'\%s' % symbol)
        res = "%s:\n*%s*" % (name, ticker)
        return res

    # context.args is list of words after command
    if not context.args:
        update.message.reply_text(
            'Use the command like this: "/find_company <company name>'
        )
        return
    name = ' '.join(context.args)
    companies = symbol_by_name(name)
    text = "\n\n".join([create_inf_line(c[0], c[1]) for c in companies])
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN_V2
    )


def main():
    # Create updater and dispather for bot
    updater = Updater(token=config.TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add handler for /start command
    dispatcher.add_handler(CommandHandler("start", start))

    # Add handler for /help command
    dispatcher.add_handler(CommandHandler("help", help_bot))

    # Create handler for /cancel command
    cancel_handler = CommandHandler("cancel", cancel)

    # Create handler for /find_company command
    dispatcher.add_handler(CommandHandler("find_company", find_company))

    # Create filter for MessageHandler
    simple_text_filter = Filters.text & ~Filters.command

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

    # Start the bot
    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()
