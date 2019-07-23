import yaml
import numpy as np
import random
import os
import math
from src.task_factory import TaskCreator, generic_task_creator
from ropod.structs.task import Task as RopodTask
from src.task import Task as GenericTask

GenericTask.__name__ = 'GenericTask'
RopodTask.__name__ = 'RopodTask'


def load_file(file):
    """ Reads a yaml file and returns a dictionary with its contents

    :param file: file to load
    :return: data as dict()
    """
    file_handle = open(file, 'r')
    data = yaml.safe_load(file_handle)
    file_handle.close()
    return data


def get_interval(interval_type, lower_bound, upper_bound):
    if interval_type == 'tight':
        interval = lower_bound
    elif interval_type == 'loose':
        interval = upper_bound
    elif interval_type == 'random':
        interval = np.random.uniform(lower_bound, upper_bound)
    else:
        raise ValueError(interval_type)

    return round(interval, 2)


def get_estimated_duration(pose_names, start_pose_name, finish_pose_name):
    # TODO: get the estimated duration from the probability distribution

    # For now, we assume constant velocity of 1 m/s
    # The estimated duration is equal to the euclidean distance

    start_coordinates = pose_names.get(start_pose_name)[:2]
    finish_coordinates = pose_names.get(finish_pose_name)[:2]

    estimated_duration = math.sqrt(sum([(a - b) ** 2 for a, b in zip(start_coordinates, finish_coordinates)]))

    return round(estimated_duration, 2)


def get_poses(pose_names):

    available_poses = dict(pose_names)

    start_pose_name = random.choice(list(available_poses.keys()))
    available_poses.pop(start_pose_name, None)

    finish_pose_name = random.choice(list(available_poses.keys()))

    return start_pose_name, finish_pose_name


class DatasetFactory(object):
    """ Registers a dataset generator based on the type of dataset that it
    generates
    """
    def __init__(self):
        self._dataset_creators = {}

    def register_dataset_creator(self, dataset_type, dataset_creator):
        self._dataset_creators[dataset_type] = dataset_creator

    def get_dataset_creator(self, dataset_type):
        dataset_creator = self._dataset_creators.get(dataset_type)
        if not dataset_creator:
            raise ValueError(dataset_type)
        return dataset_creator


def overlapping_time_windows(n_tasks, dataset_name, pose_names, **kwargs):
    """ Overlapping time windows dataset generator

     The start time interval (time between the earliest start time and the latest
     start time of a task) can be:
        - tight
        - loose
        - random

    The earliest_start_time (est) of a task is drawn from the interval
    (start_time_lower_bound, start_time_upper_bound)

    The latest_start_time (lst) of a task is the est + start interval

    The start and finish pose names are randomly chosen from the pose_names

    :param n_tasks: Number of tasks in the dataset
    :param dataset_name: Name of the new dataset
    :param pose_names: dict with pose names (keys) and poses (values)

    :param kwargs:

    interval_type (str) :   'tight', 'loose' or 'random'
                            default: 'random'

    start_time_lower_bound (int):  default: 60

    est_upper_bound (int):  default: 300

    task_generator (function): default: generic_task_generator


    :return: dataset (a dictionary of n_tasks with overlapping time windows)
    """

    interval_type = kwargs.get('interval_type', 'random')
    start_time_lower_bound = kwargs.get('lower_bound', 60)
    start_time_upper_bound = kwargs.get('upper_bound', 300)
    task_creator = kwargs.get('task_creator', generic_task_creator)

    dataset = dict()
    dataset['dataset_name'] = dataset_name
    dataset['dataset_type'] = 'overlapping_tw'
    dataset['task_type'] = task_creator.get_task_cls_name()
    dataset['tasks'] = dict()

    for i in range(0, n_tasks):
        print("Task: ", i)
        est = round(np.random.uniform(start_time_lower_bound, start_time_upper_bound), 2)
        lst = round(est +
                    get_interval(interval_type, start_time_lower_bound, start_time_upper_bound), 2)

        start_pose_name, finish_pose_name = get_poses(pose_names)

        print("est: ", est)
        print("lst: ", lst)
        print("start pose name: ", start_pose_name)
        print("finish pose name: ", finish_pose_name)

        _task_args = {'earliest_start_time': est,
                      'latest_start_time': lst,
                      'start_pose_name': start_pose_name,
                      'finish_pose_name': finish_pose_name}

        task = task_creator.create(**_task_args)

        dataset['tasks'][task.id] = task.to_dict()

    print("Dataset", dataset)

    return dataset


def non_overlapping_time_windows(n_tasks, dataset_name, pose_names, **kwargs):
    """ Non-overlapping time windows dataset generator

    The time window interval (time between tasks, i.e., the time between
    the latest finish time of a task and the earliest start time of the next
    task) can be:
        - tight
        - loose
        - random

    The earliest start time of a task (est) is the finish time of the last task
    plues the time window interval

    The duration of a task is estimated using the euclidean distance between the
    start and finish poses of the task (assuming a constant velocity of 1 m/s)

    The start and finish pose names are randomly chosen from the pose_names

    :param n_tasks: Number of tasks in the dataset
    :param dataset_name: Name of the new dataset
    :param pose_names: dict with pose names (keys) and poses (values)

    :param kwargs:

    interval_type (str) :   'tight', 'loose' or 'random'
                            default: 'random'

    start_time_lower_bound (int):  default: 60

    est_upper_bound (int):  default: 300

    task_generator (function): default: generic_task_generator


    :return: dataset (a dictionary of n_tasks with overlapping time windows)

    """

    interval_type = kwargs.get('interval_type', 'random')
    time_window_lower_bound = kwargs.get('lower_bound', 60)
    time_window_upper_bound = kwargs.get('upper_bound', 300)
    task_creator = kwargs.get('task_creator', generic_task_creator)

    dataset = dict()
    dataset['dataset_name'] = dataset_name
    dataset['dataset_type'] = 'non_overlapping_tw'
    dataset['task_type'] = task_creator.get_task_cls_name()
    dataset['tasks'] = dict()

    finish_last_task = time_window_lower_bound

    for i in range(0, n_tasks):
        print("Task: ", i)

        start_pose_name, finish_pose_name = get_poses(pose_names)

        time_window_interval = get_interval(interval_type, time_window_lower_bound, time_window_upper_bound)

        print("Finish last task: ", finish_last_task)
        print("TW Interval: ", time_window_interval)

        est = round(finish_last_task + time_window_interval, 2)
        lst = round(est +
                    get_interval(interval_type, time_window_lower_bound, time_window_upper_bound), 2)

        estimated_duration = get_estimated_duration(pose_names, start_pose_name, finish_pose_name)

        # Update finish last task
        finish_last_task = lst + estimated_duration

        print("est: ", est)
        print("lst: ", lst)
        print("start pose name: ", start_pose_name)
        print("finish pose name: ", finish_pose_name)
        print("estimated duration: ", estimated_duration)

        print("New finish last task: ", finish_last_task)

        _task_args = {'earliest_start_time': est,
                      'latest_start_time': lst,
                      'start_pose_name': start_pose_name,
                      'finish_pose_name': finish_pose_name}

        task = task_creator.create(**_task_args)

        print(task.id)

        dataset['tasks'][task.id] = task.to_dict()

    return dataset


class DatasetCreator(object):
    def __init__(self, dataset_type):

        dataset_factory = DatasetFactory()
        dataset_factory.register_dataset_creator('overlapping_tw',
                                                 overlapping_time_windows)

        dataset_factory.register_dataset_creator('non_overlapping_tw',
                                                 non_overlapping_time_windows)

        self.dataset_creator = dataset_factory.get_dataset_creator(dataset_type)

    def create(self, task_type, n_tasks, dataset_name, pose_names, **kwargs):

        task_creator = TaskCreator(task_type)
        kwargs.update({'task_creator': task_creator})

        dataset = self.dataset_creator(n_tasks, dataset_name, pose_names, **kwargs)

        return dataset

    @staticmethod
    def store(dataset, path):
        if not os.path.exists(path):
            os.mkdir(path)

        file = path + dataset.get('dataset_name') + '.yaml'

        print("File: ", file)

        with open(file, 'w') as outfile:
            yaml.safe_dump(dataset, outfile, default_flow_style=False)

