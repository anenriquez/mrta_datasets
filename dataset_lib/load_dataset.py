import csv
import os
from dataset_lib.utils.datasets import load_yaml
from dataset_lib.config.factories import task_factory
import argparse
import collections


def get_datasets_dir():
    code_dir = os.path.abspath(os.path.dirname(__file__))
    datasets_dir = code_dir + '/datasets/'

    return datasets_dir


def load_yaml_dataset(dataset_name, task_type):

    datasets_dir = get_datasets_dir()
    dataset_path = datasets_dir + dataset_name + '.yaml'
    dataset_dict = load_yaml(dataset_path)

    task_cls = task_factory.get_task_cls(task_type)

    tasks = list()
    tasks_dict = dataset_dict.get('tasks')
    ordered_tasks = collections.OrderedDict(sorted(tasks_dict.items()))

    for task_id, task_info in ordered_tasks.items():
        task = task_cls.from_dict(task_info)
        tasks.append(task)

    return tasks


def load_dataset(dataset_name, dataset_type, task_type, interval_type, file_extension):

    path = get_path_to_dataset(dataset_type, task_type, interval_type)

    if file_extension == 'yaml':

        tasks = load_yaml_dataset(dataset_name, task_type, path)

    else:
        raise ValueError(file_extension)

    return tasks


def get_path_to_dataset(dataset_type, task_type, interval_type):
    path = '/' + dataset_type + '/' + task_type \
           + '/' + interval_type + '/'
    return path


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('dataset_name', type=str, help='Name of the dataset')

    parser.add_argument('dataset_type', type=str, help='Dataset type',
                        choices=['overlapping_tw', 'non_overlapping_tw'])

    parser.add_argument('task_type', type=str, help='Task type',
                        choices=['task'],
                        default='task')

    parser.add_argument('interval_type', type=str,
                        help='Start time interval for overlapping tw'
                             'or time window interval for non_overlapping_tw',
                        choices=['tight', 'loose', 'random'])

    parser.add_argument('--file_extension', type=str, help='File extension',
                        choices=['csv', 'yaml'],
                        default='yaml')

    args = parser.parse_args()

    tasks = load_dataset(args.dataset_name, args.dataset_type, args.task_type, args.interval_type,
                         args.file_extension)

    for task in tasks:
        print(task.task_id)
        print(task.pickup_location)

