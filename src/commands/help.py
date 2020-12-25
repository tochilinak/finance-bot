from telegram import Update
from telegram.ext import CallbackContext


def help_all(update: Update):
    """Information about all commands."""
    update.message.reply_text("This is list of available commands:")
    update.message.reply_text(
        "/start - start me\n"

        "/help - get some information\n"

        "/price - get company stock price\n"

        "/find_company - find company by name. Use it if you want to know "
        "company ticker\n"

        "/add - add company to your list of companies of interest\n"

        "/delete - delete company from your list of companies of interest\n"

        "/buy and /sell - add information about your operation\n"

        "/portfolio - get information about your profit\n"

        "/operation_list - get list of your operations\n"

        "/delete_operation - delete incorrect operation\n"

        "/cancel - сancel command\n"
        
        "You can get detailed information about aome commands with "
        "/help <command_name>\n"
    )


def help_price(update: Update):
    update.message.reply_text(
        "Get information about the stock prices of companies.\n"
        "You can enter /price and enter information step by step.\n"
        "You can enter /price <tickers> and enter information about period"
        "in next message.\n"
        "<tickers> may be 'my' (for information about companies from your list"
        " of interest) or list of tickers divided by spaces.\n"
        "You can enter /price <tickers>, <period> and get information "
        "immediately\n"
        "<period> may be 'last update', 'n days' or two dates\n"
    )


def help_main(update: Update, context: CallbackContext):
    if context.args and context.args[0] == "price":
        help_price(update)
        return
    help_all(update)
