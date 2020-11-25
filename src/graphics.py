import matplotlib.pyplot as plt


def draw_plot(x_axis, y_axis, image_filename):
    """
    Draw plot and save into image_filename.svg
    
    x_axis and y_axis are lists.
    Each node (x, y) is represented by
    (x_axis[i], y_axis[i])
    """
    fig, ax = plt.subplots()
    ax.plot(x_axis, y_axis)
    plt.savefig(image_filename + ".svg", format="svg")
