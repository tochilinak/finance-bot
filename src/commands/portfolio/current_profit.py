from telegram import Update, ParseMode
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
from database import get_current_profit


def company_info_line(ticker, information):
    """Cretate string in format "ticker: profit info"."""

    result = f'*{ticker}*:\n'
    cost = str(information[0]).replace(".", r"\.")
    profit = str(information[1]).replace(".", r"\.")
    last_update = str(information[2]).replace("-", r"\-")
    result += f'actual cost: {cost}, '
    result += f'profit: {profit}\n'
    result += f'last update: {last_update}\n'
    return result


def currency_info_line(currency, information):
    """Cretate string in format "ticker: profit info"."""

    result = f'*{currency}*:\n'
    summary_cost = str(information[0]).replace(".", r"\.")
    profit = str(information[1]).replace(".", r"\.")
    result += f'summary actual costs: {summary_cost}, '
    result += f'profit: {profit}\n'
    return result


def current_profit(update: Update, context: CallbackContext):
    """Send the companies current profits to the chat"""
    chat_id = update.message.chat_id

    companies_info, currencies_info = get_current_profit(chat_id)
    print(currencies_info)
    text = "Information by company:\n"
    text += "\n".join([
        company_info_line(ticker, companies_info[ticker]) for ticker in
        companies_info.keys()])
    context.bot.send_message(
        text=text,
        chat_id=chat_id,
        parse_mode=ParseMode.MARKDOWN_V2
    )

    text = "Information by currency:\n"
    text += "\n".join([
        currency_info_line(currency, currencies_info[currency]) for currency in
        currencies_info.keys()])
    context.bot.send_message(
        text=text,
        chat_id=chat_id,
        parse_mode=ParseMode.MARKDOWN_V2
    )

    return ConversationHandler.END
