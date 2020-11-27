"""Create some filters for user messages."""
from telegram.ext import Filters

simple_text_filter = Filters.text & ~Filters.command
