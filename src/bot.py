from src.config import TOKEN
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext


def start_reaction(update: Update, context: CallbackContext):
    update.message.reply_text('lol))')


updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start_reaction))
updater.start_polling()
