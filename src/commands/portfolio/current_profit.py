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
    cost = cost.replace("-", r"\-")
    profit = str(information[1]).replace(".", r"\.")
    profit = profit.replace("-", r"\-")
    last_update = str(information[2]).replace("-", r"\-")
    result += f'actual cost: {cost}, '
    result += f'profit: {profit}\n'
    result += f'last update: {last_update}\n'
    return result


def currency_info_line(currency, information):
    """Cretate string in format "currency: profit info"."""
    result = f'*{currency}*:\n'
    summary_cost = str(information[0]).replace(".", r"\.")
    summary_cost = summary_cost.replace("-", r"\-")
    profit = str(information[1]).replace(".", r"\.")
    profit = profit.replace("-", r"\-")
    result += f'summary actual costs: {summary_cost}, '
    result += f'profit: {profit}\n'
    return result


def current_profit(update: Update, context: CallbackContext):
    """Send current profits to the chat."""
    chat_id = update.message.chat_id

    companies_info, currencies_info = get_current_profit(chat_id)

    text = "Information by company:\n"
    if companies_info:
        text += "\n".join([
            company_info_line(ticker, companies_info[ticker]) for ticker in
            companies_info.keys()])
    else:
        text += "no information"
    context.bot.send_message(
        text=text,
        chat_id=chat_id,
        parse_mode=ParseMode.MARKDOWN_V2
    )

    text = "Information by currency:\n"
    if currencies_info:
        text += "\n".join([
            currency_info_line(cur, currencies_info[cur]) for cur in
            currencies_info.keys()])
    else:
        text += "no information"
    context.bot.send_message(
        text=text,
        chat_id=chat_id,
        parse_mode=ParseMode.MARKDOWN_V2
    )

    return ConversationHandler.END
