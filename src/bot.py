from random import randint
from src.config import TOKEN
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters, ConversationHandler, MessageHandler


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello" "I am finance bot" "You can get information about commands with /help")


def help_bot(update: Update, context: CallbackContext):
    update.message.reply_text(
        "/start - start me"
        "/help - get some information"
    )


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_bot))
