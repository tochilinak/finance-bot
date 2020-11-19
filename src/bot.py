from src.config import TOKEN
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext


def start_reaction(update: Update, context: CallbackContext):
    update.message.reply_text('lol))')


def reverse_reaction(update: Update, context: CallbackContext):
    text = ' '.join(context.args)
    reversed_text = text[::-1]
    context.bot.send_message(chat_id=update.effective_chat.id, text=reversed_text)


updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start_reaction))
dispatcher.add_handler(CommandHandler('reverse', reverse_reaction))
updater.start_polling()
