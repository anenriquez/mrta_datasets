import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.dates as mdate
import matplotlib.ticker as mtick
import yaml
from math import sqrt
import os
import collections
from datetime import datetime, timedelta
import time

from src.dataset_loader import load_yaml_dataset, load_csv_dataset
from ropod.structs.task import Task as RopodTask, TaskRequest
from src.task import Task as GenericTask
GenericTask.__name__ = 'GenericTask'
RopodTask.__name__ = 'RopodTask'


def get_dataset_names(dataset_path, extension):
    dataset_names = list()

    for dataset_file in os.listdir(dataset_path):
        if dataset_file.endswith(extension):

            # Remove the extension from the name
            dataset_name = dataset_file.split('.')[0]
            dataset_names.append(dataset_name)

    return dataset_names


def load_datasets(path, task_cls, extension):

    code_dir = os.path.abspath(os.path.dirname(__file__))
    main_dir = os.path.dirname(code_dir)
    dataset_path = main_dir + path

    dataset_names = get_dataset_names(dataset_path, extension)
    datasets = dict()

    for dataset_name in dataset_names:

        if extension == '.yaml':
            tasks = load_yaml_dataset(dataset_name, task_cls, path)

        elif extension == '.csv':
            tasks = load_csv_dataset(dataset_name, task_cls, path)

        datasets[dataset_name] = tasks

    return datasets


def plot_dataset(dataset_name, tasks):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    dataset_start_time = float('inf')
    dataset_finish_time = - float('inf')

    for i, task in enumerate(tasks):
        earliest_start_time = task.earliest_start_time
        latest_finish_time = task.latest_start_time + task.estimated_duration

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
    plt.title("Temporal Distribution: Dataset " + dataset_name)

    plt.draw()
    plt.grid()
    # fig.savefig(dataset_name + "-temporal.png")

    plt.show()


if __name__ == '__main__':

    path = '/non_overlapping_tw/generictask/tight/'

    datasets = load_datasets(path, GenericTask, '.csv')

    for dataset_name, tasks in datasets.items():
        plot_dataset(dataset_name, tasks)

