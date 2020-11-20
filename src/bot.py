from random import randint
from src.config import TOKEN
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters, ConversationHandler, MessageHandler


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello" "I am finance bot")
    update.message.reply_text("You can always get list of commands with /help")
    help_bot(update, context)


def help_bot(update: Update, context: CallbackContext):
    update.message.reply_text("This is list of available commands:")
    update.message.reply_text(
        "/start - start me\n"
        "/help - get some information\n"
        "/price - get company share price\n"
    )


def company_choise_handler(fallbacks, action_after_select, next_key):
    """
    Note: action_after_select must return next_key
    """
    def stock(update: Update, context: CallbackContext):
        text = update.message.text
        context.user_data['stock'] = text
        update.message.reply_text("Ok, now enter a company ticker")
        return "company"

    def skip_stock(update: Update, context: CallbackContext):
        update.message.reply_text("Ok, just enter a company ticker")
        return "company"

    def company(update: Update, context: CallbackContext):
        text = update.message.text
        context.user_data['company'] = text
        action_after_select(update, context)
        return next_key

    handler = ConversationHandler(
        entry_points=[CommandHandler("skip", skip_stock), MessageHandler(Filters.text & ~Filters.command, stock)],
        states={
            "company": [MessageHandler(Filters.text & ~Filters.command, company)]
        },
        fallbacks=fallbacks,
        map_to_parent={
            next_key: next_key
        }
    )

    return handler


def price_start(update: Update, context: CallbackContext):
    update.message.reply_text("Ok, now I need to know the company you are interested in\n" "Enter stock name or /skip")
    update.message.reply_text("You can stop with /cancel")
    return "stock"


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("It's a shame that something went wrong")
    return ConversationHandler.END


def request_period(update: Update, context: CallbackContext):
    update.message.reply_text("Enter a period")
    return "period"


def give_price(update: Update, context: CallbackContext):
    text = update.message.text
    context.user_data['period'] = text
    update.message.reply_text("Price of " + context.user_data['company'] + " is unknown :(")
    return ConversationHandler.END


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_bot))
    cancel_handler = CommandHandler("cancel", cancel)
    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("price", price_start)],
            states={
                "stock": [company_choise_handler([cancel_handler], request_period, "period")],
                "period": [MessageHandler(Filters.text & ~Filters.command, give_price)]
            },
            fallbacks=[cancel_handler]
        )
    )

    updater.start_polling()


if __name__ == "__main__":
    main()
