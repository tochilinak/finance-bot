import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateLocator, AutoDateFormatter


my_scaled = {
    365.0: '%Y',
    30.0: '%Y-%m',
    1: '%Y-%m-%d',
    1 / 24: '%H:%M',
}


def draw_plot(datetime_values, y_values, image_filename):
    """
    Draw plot and save into image_filename.svg.

    datetime_values is a list of datetime objects,
    y_values is a list of int.
    Each node's coordinates (x, y) are:
    (datetime_values[i], y_values[i])
    """
    fig, ax = plt.subplots()
    ax.plot(datetime_values, y_values)
    locator = AutoDateLocator()
    formatter = AutoDateFormatter(locator)
    formatter.scaled = my_scaled
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    fig.autofmt_xdate()

    plt.savefig(image_filename + ".svg", format="svg")
