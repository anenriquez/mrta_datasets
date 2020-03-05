import argparse
from datetime import datetime

import dateutil.parser
import matplotlib.dates as mdate
import matplotlib.pyplot as plt
from dataset_lib.load_dataset import load_yaml_dataset
from matplotlib.patches import Rectangle


def plot_dataset(dataset_name, tasks, show=False):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    dataset_start_time = float('inf')
    dataset_finish_time = - float('inf')
    highest_set_number = 0
    earliest_task = None

    iso_time = "2020-01-23T08:00:00.000000"
    start_time = dateutil.parser.parse(iso_time).timestamp()

    for task in tasks:
        earliest_start_time = task.earliest_pickup_time + start_time
        latest_finish_time = task.latest_pickup_time + task.plan.estimated_duration + start_time

        if task.set_number > highest_set_number:
            highest_set_number = task.set_number

        if earliest_start_time < dataset_start_time:
            dataset_start_time = earliest_start_time
            earliest_task = task

        if latest_finish_time > dataset_finish_time:
            dataset_finish_time = latest_finish_time

        # Convert form epoch to datetime object
        start_window = datetime.fromtimestamp(earliest_start_time)
        end_window = datetime.fromtimestamp(latest_finish_time)

        # convert to matplotlib date representation
        start_rectangle = mdate.date2num(start_window)
        end_rectangle = mdate.date2num(end_window)
        width_rectangle = end_rectangle - start_rectangle

        rect = Rectangle((start_rectangle, task.set_number), width_rectangle, 0.2, color='blue')
        ax.add_patch(rect)

        rx, ry = rect.get_xy()
        cx = rx + rect.get_width() / 2.0
        cy = ry + rect.get_height() / 2.0

        ax.annotate(task.task_id[:3], (cx, cy), color='w', weight='bold',
                    fontsize=6, ha='center', va='center')

    start_time = mdate.date2num(datetime.fromtimestamp(dataset_start_time))
    finish_time = mdate.date2num(datetime.fromtimestamp(dataset_finish_time))

    date_fmt = '%H:%M:%S'
    # Use a DateFormatter to set the data to the correct format.
    date_formatter = mdate.DateFormatter(date_fmt)
    ax.xaxis.set_major_formatter(date_formatter)

    # Sets the tick labels diagonal so they fit easier.
    fig.autofmt_xdate()
    # set the limits
    plt.xlim([start_time - width_rectangle, finish_time + width_rectangle])
    plt.ylim([0, highest_set_number + 1])

    plt.xlabel("Time (hours:minutes:seconds)")
    plt.ylabel("Task set number")
    plt.title("Dataset: " + dataset_name)

    print("Earliest task: ", earliest_task.task_id)

    plt.draw()
    plt.grid()

    if show:
        plt.show()

    return fig


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('dataset_name', type=str, help='Name of the dataset')

    parser.add_argument('--task_type', type=str, help='Task type', choices=['task'], default='task')

    args = parser.parse_args()

    dataset = load_yaml_dataset(args.dataset_name, args.task_type)

    fig = plot_dataset(args.dataset_name, dataset['tasks'])
    fig.savefig('datasets/plots/' + args.dataset_name + '.png')


