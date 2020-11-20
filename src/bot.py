from random import randint
from src.config import TOKEN
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext


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


updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

updater.job_queue.run_repeating(callback=update_ri, interval=10, context=randint(1, 10), name="ri_updater")

dispatcher.add_handler(CommandHandler('start', start_reaction))
dispatcher.add_handler(CommandHandler('ri', ri_reaction))
dispatcher.add_handler(CommandHandler('reverse', reverse_reaction))
updater.start_polling()
