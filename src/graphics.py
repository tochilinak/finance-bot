import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateLocator, AutoDateFormatter

"""
Usage example:

from api_requests import get_period_data_of_cost

dates, values = get_period_data_of_cost("2015-10-01",
                                        "2020-11-20", "GAZP")
draw_plot(dates, values, "out.png", currency="RUB",
          title="Some plot")
"""


def set_small_data_labels(datetime_values, ax):
    ax.set_xticks(datetime_values)
    # check whether datetimes represent dates or time
    if all(x.hour == 0 and x.minute == 0 for x in datetime_values):
        labels = [x.strftime('%Y-%m-%d') for x in datetime_values]
    else:
        labels = [x.strftime('%H:%M') for x in datetime_values]
    ax.set_xticklabels(labels)


my_scaled = {
    365.0: '%Y',
    30.0: '%Y-%m',
    1: '%Y-%m-%d',
    1 / 24: '%H:%M',
}


def set_big_data_labels(ax):
    locator = AutoDateLocator()
    formatter = AutoDateFormatter(locator)
    formatter.scaled = my_scaled
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)


DAYS_IN_WEEK = 7
DAYS_IN_MONTH = 30  # roughly


def set_labels(datetime_values, ax):
    if len(datetime_values) < DAYS_IN_WEEK:
        set_small_data_labels(datetime_values, ax)
    else:
        set_big_data_labels(ax)


def draw_plot(datetime_values, y_values, image_filename,
              title=None, currency=None):
    """
    Draw plot and save into image_filename.

    datetime_values is a list of datetime objects,
    y_values is a list of int.
    Each node's coordinates (x, y) are:
    (datetime_values[i], y_values[i])
    """
    fig, ax = plt.subplots()
    fig.subplots_adjust(left=0.2)
    ax.plot(datetime_values, y_values)
    # add big dots if data is small
    if len(datetime_values) <= DAYS_IN_MONTH:
        ax.plot_date(datetime_values, y_values)
    set_labels(datetime_values, ax)
    fig.autofmt_xdate()

    ylabel = "stock price"
    if currency is not None:
        ylabel += f" (in {currency})"
    ax.set_ylabel(ylabel)

    if title is not None:
        ax.set_title(title)

    plt.savefig(image_filename, format="png")
