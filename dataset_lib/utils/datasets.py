""" Includes methods to prepare and write dataset files
"""

import csv
from pathlib import Path
import yaml
import collections


def load_yaml(file):
    """ Reads a yaml file and returns a dictionary with its contents

    :param file: file to load
    :return: data as dict()
    """
    with open(file, 'r') as file:
        data = yaml.safe_load(file)
    return data


def flatten_dict(dict_input):
    """ Returns a dictionary without nested dictionaries

    :param dict_input: nested dictionary
    :return: flattened dictionary

    """
    flattened_dict = dict()

    for key, value in dict_input.items():
        if isinstance(value, dict):
            new_keys = sorted(value.keys())
            for new_key in new_keys:
                entry = {key + '_' + new_key: value[new_key]}
                flattened_dict.update(entry)
        else:
            entry = {key: value}
            flattened_dict.update(entry)

    return flattened_dict


def keep_entry(dict_input, parent_key, child_keys):
    """
    Keeps child_keys in dict_input and not other entries that start with the same parent_key

    :param dict_input:
    :param parent_key: string
    :param child_keys: list of strings
    :return: dictionary with removed child keys
    """

    dict_output = dict()

    child_keys = [''.join((parent_key, '_', child_key)) for child_key in child_keys]

    for key, value in dict_input.items():
        if key.startswith(parent_key) and key not in child_keys:
            pass
        else:
            dict_output.update({key: value})

    return dict_output


def to_csv(list_dicts, file_name):
    """ Exports a list of dictionaries to a csv file

    :param list_dicts: list of dictionaries to be exported
    :param file_name: name of the csv file

    """
    # We assume that all the dictionaries have the same keys
    fieldnames = list_dicts[0].keys()

    with open(file_name, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames)
        dict_writer.writeheader()
        dict_writer.writerows(list_dicts)


def store_as_yaml(dataset, path):
    """ Receives a dictionary (in yaml format) and stores it as yaml in path

    :param dataset: dictionary of tasks
    :param path: path where the dataset will be stored
    """
    dataset_path = str(Path.cwd()) + path

    # Create path if it doesn't exist
    Path(dataset_path).mkdir(parents=True, exist_ok=True)

    file = dataset_path + dataset.get('dataset_name') + '.yaml'
    open(dataset_path + '__init__.py', "w+")

    with open(file, 'w') as outfile:
        yaml.safe_dump(dataset, outfile, default_flow_style=False)


def store_as_csv(dataset, task_cls, path):
    """ Receives a dictionary (in yaml format) and saves it
    as a csv file in path

    :param dataset: dictionary of tasks
    :param task_cls: class of tasks in dataset
    :param path: path where the dataset will be stored
    :return:
    """
    dataset_path = str(Path.cwd()) + path

    # Create path if it doesn't exist
    Path(dataset_path).mkdir(parents=True, exist_ok=True)

    file = dataset_path + dataset.get('dataset_name') + '.csv'

    tasks = dataset.get('tasks')
    list_task_dicts = list()

    ordered_tasks = collections.OrderedDict(sorted(tasks.items()))

    for task_id, task in ordered_tasks.items():
        csv_dict = task_cls.to_csv(task)
        list_task_dicts.append(csv_dict)

    to_csv(list_task_dicts, file)