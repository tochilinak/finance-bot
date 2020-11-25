import matplotlib.pyplot as plt


def draw_plot(datetime_values, y_values, image_filename):
    """
    Draw plot and save into image_filename.svg

    datetime_values is a list of datetime objects,
    y_values is a list of int.
    Each node's coordinates (x, y) are:
    (datetime_values[i], y_values[i])
    """
    fig, ax = plt.subplots()
    ax.plot(datetime_values, y_values)
    fig.autofmt_xdate()
    plt.savefig(image_filename + ".svg", format="svg")
