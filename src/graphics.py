import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateLocator, AutoDateFormatter
from dataclasses import dataclass
from datetime import datetime
from typing import List

"""
Usage example:

from api_requests import get_period_data_of_cost

dates, values = get_period_data_of_cost("2015-10-01",
                                        "2020-11-20", "GAZP")
draw_plot(dates, values, "out.png", currency="RUB",
          title="Some plot")
"""


@dataclass
class PlotData:
    dates: List[datetime]
    y_values: List[int]
    title: str = None
    currency: str = None

    def __post_init__(self):
        assert len(self.dates) == len(self.y_values)


def set_small_data_labels(dates, ax):
    ax.set_xticks(dates)
    # check whether datetimes represent dates or time
    if all(x.hour == 0 and x.minute == 0 for x in dates):
        labels = [x.strftime('%Y-%m-%d') for x in dates]
    else:
        labels = [x.strftime('%H:%M') for x in dates]
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


def set_labels(dates, ax):
    if len(dates) < DAYS_IN_WEEK:
        set_small_data_labels(dates, ax)
    else:
        set_big_data_labels(ax)


def draw_cell(plot_data, image_filename, fig, ax):
    fig.subplots_adjust(left=0.2)
    ax.plot(plot_data.dates, plot_data.y_values)

    # add big dots if data is small
    if len(plot_data.dates) <= DAYS_IN_MONTH:
        ax.plot_date(plot_data.dates, plot_data.y_values)

    set_labels(plot_data.dates, ax)
    fig.autofmt_xdate()

    ylabel = "stock price"
    if plot_data.currency is not None:
        ylabel += f" (in {plot_data.currency})"
    ax.set_ylabel(ylabel)

    if plot_data.title is not None:
        ax.set_title(plot_data.title)


def draw_plot(plot_data, image_filename):
    """
    Draw plot and save into image_filename.

    datetime_values is a list of datetime objects,
    y_values is a list of int.
    Each node's coordinates (x, y) are:
    (datetime_values[i], y_values[i])
    """
    fig, ax = plt.subplots()
    draw_cell(plot_data, image_filename, fig, ax)
    plt.savefig(image_filename, format="png")
