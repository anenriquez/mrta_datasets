import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.dates as mdate
import os
from datetime import datetime
import argparse
from pathlib import Path
from dataset_lib.load_dataset import load_yaml_dataset, get_path_to_dataset
from dataset_lib.utils.datasets import load_yaml


def plot_dataset(dataset_name, tasks, show=False):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    dataset_start_time = float('inf')
    dataset_finish_time = - float('inf')
    now = datetime.now().timestamp()

    for i, task in enumerate(tasks):
        earliest_start_time = task.earliest_pickup_time + now
        latest_finish_time = task.latest_pickup_time + task.plan.estimated_duration + now

        if earliest_start_time < dataset_start_time:
            dataset_start_time = earliest_start_time

        if latest_finish_time > dataset_finish_time:
            dataset_finish_time = latest_finish_time

        # Convert form epoch to datetime object
        start_window = datetime.fromtimestamp(earliest_start_time)
        end_window = datetime.fromtimestamp(latest_finish_time)

        # convert to matplotlib date representation
        start_rectangle = mdate.date2num(start_window)
        end_rectangle = mdate.date2num(end_window)
        width_rectangle = end_rectangle - start_rectangle

        rect = Rectangle((start_rectangle, i+1), width_rectangle, 0.2, color='blue')
        ax.add_patch(rect)

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
    plt.ylim([0, len(tasks) + 1])

    plt.xlabel("Time (hours:minutes:seconds)")
    plt.ylabel("Task number")
    plt.title("Dataset: " + dataset_name)

    plt.draw()
    plt.grid()

    if show:
        plt.show()

    return fig


def save_plot(fig, dataset_name):
    code_dir = os.path.abspath(os.path.dirname(__file__))
    main_dir = os.path.dirname(code_dir)

    # path = get_path_to_dataset(dataset_type, task_type, interval_type)

    plot_path = code_dir + '/datasets' + dataset_name + '.yaml'

    # Create path if it doesn't exist
    # Path(plot_path).mkdir(parents=True, exist_ok=True)

    fig.savefig(dataset_name + ".png")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('dataset_name', type=str, help='Name of the dataset')

    # parser.add_argument('dataset_type', type=str, help='Dataset type',
    #                     choices=['overlapping_tw', 'non_overlapping_tw'])
    #
    parser.add_argument('--task_type', type=str, help='Task type', choices=['task'], default='task')
    #
    # parser.add_argument('interval_type', type=str,
    #                     help='Start time interval for overlapping tw'
    #                     'or time window interval for non_overlapping_tw',
    #                     choices=['tight', 'loose', 'random'])
    #
    # parser.add_argument('--file_extension', type=str, help='File extension',
    #                     choices=['csv', 'yaml'],
    #                     default='yaml')

    args = parser.parse_args()

    tasks = load_yaml_dataset(args.dataset_name, args.task_type)

    fig = plot_dataset(args.dataset_name, tasks)
    fig.savefig('datasets/plots/' + args.dataset_name + '.png')
    # save_plot(fig, args.dataset_name)


