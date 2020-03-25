import argparse
import os
import random
from datetime import datetime
from datetime import timedelta

import dateutil.parser
import dateutil.parser
import matplotlib.dates as mdate
import matplotlib.pyplot as plt
from dataset_lib.load_dataset import load_yaml_dataset
from matplotlib.patches import Rectangle
from plotly import figure_factory as ff


def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


def get_color():
    return 'rgb(52, 70, 235)'


def get_colors(gantt_tasks):
    return {task.get('Resource'): get_color() for task in gantt_tasks}


def plot_gantt(title, schedule, colors, group_tasks=True, borders=False, **kwargs):
    directory = kwargs.get('dir', 'datasets/plots/')
    xmin = kwargs.get('xmin')
    xmax = kwargs.get('xmax')
    show = kwargs.get('show')

    fig = ff.create_gantt(schedule, title="Dataset: " + title, group_tasks=group_tasks, showgrid_x=True,
                          index_col='Resource', colors=colors)
    if borders:
        # Taken from https://community.plotly.com/t/borders-in-gantt-charts/32030
        fig.update_traces(mode='lines', line_color='rgb(229, 236, 246)', selector=dict(fill='toself'))

    if xmin and xmax:
        fig.layout.xaxis.update(range=[xmin, xmax])

    if not os.path.exists(directory):
        os.makedirs(directory)

    fig.write_image(directory + '/%s.png' % title)
    fig.write_html(directory + '/%s.html' % title)
    if show:
        fig.show()


def get_gantt_task(task_id, pickup_time, delivery_time, set_number):
    return [
        dict(Task=set_number, Start=pickup_time, Finish=delivery_time, Resource=task_id)
    ]


def plot_dataset_plotly(dataset_name, tasks, initial_time, show=False):
    """
    Args:
        dataset_name (str) name of dataset
        tasks (list) of Tasks
        initial_time (iso_time): Initial time to which tasks are referenced to
        e.g. "2020-01-23T08:00:00.000000"

    """
    gantt_tasks = list()
    initial_time = dateutil.parser.parse(initial_time).timestamp()
    earliest_time = float('inf')
    latest_time = - float('inf')

    for task in tasks:
        pickup_time = task.earliest_pickup_time + initial_time
        delivery_time = task.latest_pickup_time + initial_time + task.plan.estimated_duration
        gantt_tasks += get_gantt_task(task.task_id,
                                      datetime.fromtimestamp(pickup_time),
                                      datetime.fromtimestamp(delivery_time),
                                      task.set_number)

        if pickup_time < earliest_time:
            earliest_time = pickup_time

        if delivery_time > latest_time:
            latest_time = delivery_time

    xmin = datetime.fromtimestamp(earliest_time) - timedelta(seconds=60)
    xmax = datetime.fromtimestamp(latest_time) + timedelta(seconds=60)

    colors = get_colors(gantt_tasks)

    plot_gantt(dataset_name, gantt_tasks, colors, xmin=xmin, xmax=xmax, show=show)


def plot_dataset_plt(dataset_name, tasks, initial_time, show=False, **kwargs):
    directory = kwargs.get('dir', 'datasets/plots/')
    fig = plt.figure()
    ax = fig.add_subplot(111)

    dataset_start_time = float('inf')
    dataset_finish_time = - float('inf')
    highest_set_number = 0
    earliest_task = None

    start_time = dateutil.parser.parse(initial_time).timestamp()

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

    fig.savefig(directory + args.dataset_name + '.png')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('dataset_name', type=str, help='Name of the dataset')

    parser.add_argument('--task_type', type=str, help='Task type', choices=['task'], default='task')

    initial_time = "2020-01-23T08:00:00.000000"

    args = parser.parse_args()

    dataset = load_yaml_dataset(args.dataset_name, args.task_type)

    plot_dataset_plotly(args.dataset_name, dataset['tasks'], initial_time)




