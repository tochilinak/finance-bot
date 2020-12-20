from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext
)
import config
from commands.price.price import price_handler
from commands.find_company import find_company_handler
from commands.list_of_interesting.add import add_to_list_handler
from commands.list_of_interesting.delete import delete_from_list_handler
from commands.portfolio.operation import buy_handler, sell_handler
from commands.portfolio.portfolio import portfolio_handler
from commands.basic import (
    unknown_command_handler,
    unknown_text_handler
)


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

        "/add - add company to your list of companies of interest\n"

        "/delete - delete company from your list of companies of interest\n"

        "/cancel - сancel command\n"
    )


def main():
    # Create updater and dispather for bot
    updater = Updater(token=config.TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add handler for /start command
    dispatcher.add_handler(CommandHandler("start", start))

    # Add handler for /help command
    dispatcher.add_handler(CommandHandler("help", help_bot))

    # Add conversation handler for /price command
    dispatcher.add_handler(price_handler)

    # Add conversation handler for /find_company command
    dispatcher.add_handler(find_company_handler)

    # Add conversation handlers for /add and /delete commands
    dispatcher.add_handler(add_to_list_handler)
    dispatcher.add_handler(delete_from_list_handler)

    # Add handlers for buy and sell
    dispatcher.add_handler(buy_handler)
    dispatcher.add_handler(sell_handler)

    # Add handler for /portfolio
    dispatcher.add_handler(portfolio_handler)

    # Add handlers for unknown messages
    dispatcher.add_handler(unknown_command_handler)
    dispatcher.add_handler(unknown_text_handler)

    # Start the bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
