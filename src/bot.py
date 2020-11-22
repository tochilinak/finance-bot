from random import randint
from src.config import TOKEN
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters, ConversationHandler, MessageHandler


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello\n" "I am finance bot")
    update.message.reply_text("You can always get list of commands with\n /help")
    help_bot(update, context)


def help_bot(update: Update, context: CallbackContext):
    update.message.reply_text("This is list of available commands:")
    update.message.reply_text(
        "/start - start me\n"
        "/help - get some information\n"
        "/price - get company stock price\n"
    )


def price_start(update: Update, context: CallbackContext):
    update.message.reply_text("Ok, now I need to know the company you are interested in\n" "Enter a company ticker ")
    update.message.reply_text("You can stop with /cancel")
    return "company"


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("It's a shame that something went wrong")
    return ConversationHandler.END


def get_company(update: Update, context: CallbackContext):
    text = update.message.text
    context.job_queue.run_once(
        callback=give_price,
        when=0,
        context={'chat_id': update.message.chat.id, "company": text}
    )
    return ConversationHandler.END


def give_price(context: CallbackContext):
    job_context = context.job.context
    company = job_context["company"]
    chat_id = job_context["chat_id"]
    message_text = company + " is misterious for me"  # вот тут нужно найти цену
    context.bot.send_message(
        chat_id=chat_id,
        text=message_text
    )


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
                "company": [MessageHandler(Filters.text & ~Filters.command, get_company)],
            },
            fallbacks=[cancel_handler]
        )
    )

    updater.start_polling()


if __name__ == "__main__":
    main()
