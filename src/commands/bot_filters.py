"""Create some filters for user messages."""
from telegram.ext import Filters

simple_text_filter = Filters.text & ~Filters.command
se_dates_filter = Filters.regex(r'h')
command_filter = Filters.command
