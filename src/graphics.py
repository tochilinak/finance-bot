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
plot_data = PlotData(dates, values, title="GAZP Plot", currency="RUB")
draw_plot(plot_data, "out.png")
"""


@dataclass
class PlotData:
    """Class for storing data needed to draw plot."""

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


def draw_cell(plot_data, ax):
    ax.plot(plot_data.dates, plot_data.y_values)

    # add big dots if data is small
    if len(plot_data.dates) <= DAYS_IN_MONTH:
        ax.plot_date(plot_data.dates, plot_data.y_values)

    set_labels(plot_data.dates, ax)

    ylabel = "stock price"
    if plot_data.currency is not None:
        ylabel += f" (in {plot_data.currency})"
    ax.set_ylabel(ylabel)

    if plot_data.title is not None:
        ax.set_title(plot_data.title)

    for tick in ax.get_xticklabels():
        tick.set_visible(True)


def draw_plot(plot_data, image_filename):
    """
    Draw plot and save into image_filename.

    :plot_data: PlotData object.
    """
    fig, ax = plt.subplots(num)
    draw_cell(plot_data, ax)

    fig.subplots_adjust(left=0.2)
    fig.autofmt_xdate()

    plt.savefig(image_filename, format="png")


def choose_size(plot_num):
    n = int(plot_num ** 0.5 + 0.5)
    m = (plot_num + n - 1) // n
    return n, m


def draw_multiplot(plot_data_list, image_filename):
    """
    Draw several plots in one image and save into image_filename.

    :plot_data_list: list of PlotData objects
    """
    num = len(plot_data_list)

    if num == 1:
        draw_plot(plot_data_list[0], image_filename)
        return

    n, m = choose_size(num)
    fig, axs = plt.subplots(n, m, figsize=(3.2 * m, 2.4 * n),
                            sharex=False)

    for i in range(num):
        draw_cell(plot_data_list[i], axs.flat[i])

    fig.autofmt_xdate()
    fig.tight_layout()

    plt.savefig(image_filename, format="png")
