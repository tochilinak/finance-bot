"""Create some filters for user messages."""
from telegram.ext import Filters

# Pattern for dates in format YYYY-MM-DD YYYY-MM-DD
se_dates = r'^\d{4}-\d{2}-\d{2} \d{4}-\d{2}-\d{2}$'
se_dates_filter = Filters.regex(se_dates)

# Pattern for string in format "_ days"
some_days = r'^\d+ days$'
some_days_filter = Filters.regex(some_days)

simple_text_filter = Filters.text & ~Filters.command

command_filter = Filters.command
