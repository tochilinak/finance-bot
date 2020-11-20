from random import randint
from src.config import TOKEN
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters, ConversationHandler, MessageHandler


def start_reaction(update: Update, context: CallbackContext):
    update.message.reply_text('lol))')


def reverse_reaction(update: Update, context: CallbackContext):
    text = ' '.join(context.args)
    reversed_text = text[::-1]
    context.bot.send_message(chat_id=update.effective_chat.id, text=reversed_text)


def update_ri(context: CallbackContext):
    context.job.context = randint(1, 10)


def ri_reaction(update: Update, context: CallbackContext):
    ri_updater = context.job_queue.get_jobs_by_name("ri_updater")[0]
    ri = ri_updater.context
    update.message.reply_text(str(ri))


SELECT_ACTION, SELECT_COMPANY_CONVERSATION, SELECT_STOCK, SELECT_COMPANY = range(4)
END = ConversationHandler.END


def start_conv(update: Update, context: CallbackContext):
    update.message.reply_text('Hi! What do you want?')
    return SELECT_ACTION


def action_choise(update: Update, context: CallbackContext):
    text = update.message.text
    if text == "price":
        update.message.reply_text("Ok, now I need company name")
        return SELECT_COMPANY
    else:
        update.message.reply_text("I don't inderstand")
        return SELECT_ACTION


def company_choise(update: Update, context: CallbackContext):
    company = update.message.text
    update.message.reply_text(company + " is misterious for me")
    return END


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Bye!")
    return END


updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

updater.job_queue.run_repeating(callback=update_ri, interval=10, context=randint(1, 10), name="ri_updater")

main_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start_conv", start_conv)],
    states={
        SELECT_ACTION: [MessageHandler(Filters.text & ~Filters.command, action_choise)],
        SELECT_COMPANY: [MessageHandler(Filters.text & ~Filters.command, company_choise)]
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)
dispatcher.add_handler(main_conv_handler)
dispatcher.add_handler(CommandHandler('start', start_reaction))
dispatcher.add_handler(CommandHandler('ri', ri_reaction))
dispatcher.add_handler(CommandHandler('reverse', reverse_reaction))
updater.start_polling()
