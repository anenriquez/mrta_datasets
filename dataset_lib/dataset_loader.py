import csv
import os
from dataset_lib.utils.datasets import load_yaml
from dataset_lib.task_factory import TaskLoader
import argparse
from dataset_lib.task_factory import initialize_task_factory
import collections


def get_datasets_dir():
    code_dir = os.path.abspath(os.path.dirname(__file__))
    main_dir = os.path.dirname(code_dir)

    datasets_dir = main_dir + '/datasets'

    return datasets_dir


def load_csv_dataset(dataset_name, task_type, path):

    datasets_dir = get_datasets_dir()

    dataset_path = datasets_dir + path + dataset_name + '.csv'

    tasks = list()

    task_loader = TaskLoader()

    try:
        with open(dataset_path, 'r') as file:
            csv_reader = csv.DictReader(file)

            for task_csv in csv_reader:
                task = task_loader.load_csv(task_type, task_csv)

                tasks.append(task)

    except IOError:
        print("File does not exist")

    return tasks


def load_yaml_dataset(dataset_name, task_type, path):

    datasets_dir = get_datasets_dir()

    dataset_path = datasets_dir + path + dataset_name + '.yaml'

    dataset_dict = load_yaml(dataset_path)

    task_factory = initialize_task_factory()
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

    if file_extension == 'csv':

        tasks = load_csv_dataset(dataset_name, task_type, path)

    elif file_extension == 'yaml':

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
                        choices=['generic_task', 'ropod_task', 'task_request'])

    parser.add_argument('interval_type', type=str,
                        help='Start time interval for overlapping tw'
                             'or time window interval for non_overlapping_tw',
                        choices=['tight', 'loose', 'random'])

    parser.add_argument('file_extension', type=str, help='File extension',
                        choices=['csv', 'yaml'])

    args = parser.parse_args()

    tasks = load_dataset(args.dataset_name, args.dataset_type, args.task_type, args.interval_type,
                         args.file_extension)

    for task in tasks:
        print(task.task_id)

