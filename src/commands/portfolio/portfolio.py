from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackContext,
    ConversationHandler
)
from commands.basic import default_fallbacks, default_map_to_parent
from commands.period import PeriodGetter
from commands.portfolio.current_profit import current_profit
from commands.portfolio.period_profit import period_profit


def give_portfolio(update: Update, context: CallbackContext):
    """Act after getting information about the period."""
    period = context.user_data["period"]
    if period.period_type == "lu":
        return current_profit(update, context)
    if period.period_type == "cd":
        return period_profit(update, context)
    update.message.reply_text("Something went wrong")
    return ConversationHandler.END


PERIOD_GETTER = PeriodGetter(give_portfolio, default_map_to_parent)


def portfolio_start(update: Update, context: CallbackContext):
    """
    Srart of conversation.

    User can enter /portfolio <period> or just /portfolio
    """
    # /portfolio is useless part of message now
    update.message.text = update.message.text[11:]
    return PERIOD_GETTER.start_getting_period()(update, context)


portfolio_handler = ConversationHandler(
    entry_points=[CommandHandler("portfolio", portfolio_start)],
    states={
        "period": [PERIOD_GETTER.get_period_handler()]
    },
    fallbacks=default_fallbacks
)
