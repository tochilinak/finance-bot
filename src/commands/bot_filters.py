"""Create some filters for user messages."""
from telegram.ext import Filters

simple_text_filter = Filters.text & ~Filters.command
se_dates_filter = Filters.regex(r'^\d{4}-\d{2}-\d{2} \d{4}-\d{2}-\d{2}$')
command_filter = Filters.command
