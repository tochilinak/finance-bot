from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    CommandHandler,
    MessageHandler
)
from re import match
from datetime import datetime, timedelta
from commands.basic import default_fallbacks
from commands.bot_filters import (se_dates, some_days, se_dates_filter,
                                  some_days_filter, simple_text_filter)


class Period:
    """Classs for information about period entered by user."""

    def __init__(self, period_type, data=None):
        self.period_type = period_type
        self.data = data


class PeriodGetter:
    """Class for writing Period in user data."""

    def __init__(self, callback, map_to_parent):
        """
        Create Getter.

        :param callback: function, that will be called after getting a period.
        It can be 'return "got_period"' if you need to go to next state of
        conversation or function that gives user information and end the
        conversation.
        :param map_to_parent: map to parent conversation.
        Example: {"got_period": "got_period", "back_to_ticker": "ticker",
        "END": ConversationHandler.END}
        """
        self.callback = callback
        self.map_to_parent = map_to_parent

    @staticmethod
    def create_last_update_period(context: CallbackContext, text: str):
        """Try to write information about lust_update period to user data."""
        if match(r'^last.update$', text):
            context.user_data["period"] = Period("lu")
            return True
        return False

    @staticmethod
    def create_custom_period(context: CallbackContext, text: str):
        """Try to write information about custom period to user data."""
        if match(se_dates, text):
            context.user_data["period"] = Period("cd", text)
            return True
        return False

    @staticmethod
    def create_some_days_period(context: CallbackContext, text: str):
        """Try to write information about 'n days' period to user data."""
        if match(some_days, text):
            numebr_of_days = text.split(' ')[0]
            today = datetime.now().date()
            start_date = today - timedelta(days=int(numebr_of_days))
            text = " ".join([str(start_date), str(today)])
            context.user_data["period"] = Period("cd", text)
            return True
        return False

    @staticmethod
    def is_number(text: str):
        if match(r"\d+$", text):
            return True
        return False

    @staticmethod
    def ask_period(update: Update):
        """Ask about period (send some messages)."""
        update.message.reply_text(
            "What period are you interested in?"
        )
        update.message.reply_text(
            "You can get information about entering "
            "a period with the /periods command"
        )
        return "period"

    def start_getting_period(self):
        """Start getting period if it is not specified in message."""

        def res(update: Update, context: CallbackContext):
            text = update.message.text
            if text is None:
                return PeriodGetter.ask_period(update)
            else:
                if PeriodGetter.create_custom_period(context, text):
                    # now period is in user_data["period"] and we can go
                    return self.callback(update, context)
                if PeriodGetter.create_some_days_period(context, text):
                    # now period is in user_data["period"] and we can go
                    return self.callback(update, context)
                if PeriodGetter.create_last_update_period(context, text):
                    # now period is in user_data["period"] and we can go
                    return self.callback(update, context)
                return PeriodGetter.ask_period(update)

        return res

    @staticmethod
    def periods(update: Update, context: CallbackContext):
        """Give user information about entering a period."""
        update.message.reply_text(
            "/last_update - get the most current information available\n"
            "/custom - get information for a specified period of time\n"
            "/days - get information for last n days\n"
        )
        return "period"

    def last_update(self):
        """Create function with action from self.callback."""
        def res(update: Update, context: CallbackContext):
            """Reaction to /last_update."""
            context.user_data["period"] = Period("lu")
            return self.callback(update, context)

        return res

    @staticmethod
    def custom(update: Update, context: CallbackContext):
        """Reaction to /custom. Ask dates for custom request."""
        update.message.reply_text(
            "Enter start and end date, format 'YYYY-MM-DD YYYY-MM-DD'"
        )

        update.message.reply_text(
            "You can just enter two dates after the ticker message next time "
            "(and not use /custom)"
        )

        return "get_custom_period"

    def get_custom_period(self):
        """Create function with action from self.callback."""
        def res(update: Update, context: CallbackContext):
            """Create custom period from message text."""
            text = update.message.text
            if PeriodGetter.create_custom_period(context, text):
                return self.callback(update, context)

            update.message.reply_text(
                "Try again, format 'YYYY-MM-DD YYYY-MM-DD'"
            )
            return "get_custom_period"

        return res

    @staticmethod
    def days(update: Update, context: CallbackContext):
        """Reaction to /days. Ask number of days for request."""
        update.message.reply_text(
            "Enter number of days"
        )

        update.message.reply_text(
            "You can just enter 'n days' after the ticker message next time "
            "(and not use /days)"
        )

        return "get_number_of_days"

    def get_number_of_days(self):
        """Create function with action from self.callback."""
        def res(update: Update, context: CallbackContext):
            """Create custom period from text in 'n days' format."""
            text = update.message.text
            if PeriodGetter.create_some_days_period(context, text):
                return self.callback(update, context)
            if PeriodGetter.is_number(text):
                PeriodGetter.create_some_days_period(context, text + " days")
                return self.callback(update, context)

            update.message.reply_text(
                "Try again, enter number of days"
            )
            return "get_number_of_days"

        return res

    def independent_handlers(self):
        """Handlers that can be entry point."""
        return [
            CommandHandler("periods", PeriodGetter.periods),
            CommandHandler("days", PeriodGetter.days),
            CommandHandler("custom", PeriodGetter.custom),
            CommandHandler("last_update", self.last_update()),
            MessageHandler(some_days_filter, self.get_number_of_days()),
            MessageHandler(se_dates_filter, self.get_custom_period())
        ]

    def get_period_handler(self):
        """Create conversation hanler for getting period."""
        return ConversationHandler(
            entry_points=self.independent_handlers(),
            states={"period": self.independent_handlers(),
                    "get_custom_period": [
                        MessageHandler(simple_text_filter,
                                       self.get_custom_period())],
                    "get_number_of_days": [
                        MessageHandler(simple_text_filter,
                                       self.get_number_of_days())
                    ]
                    },
            fallbacks=default_fallbacks,
            map_to_parent=self.map_to_parent
        )
