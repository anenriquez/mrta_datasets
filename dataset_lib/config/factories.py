from importlib import import_module
import logging

import numpy as np

from dataset_lib.utils.uuid import generate_uuid


class TaskFactory:
    def __init__(self):
        self._task_cls = {}

    def register_task_cls(self, task_type, task_cls):
        self._task_cls[task_type] = task_cls

    def get_task_cls(self, task_type):
        task_cls = self._task_cls.get(task_type)
        if not task_cls:
            raise ValueError(task_type)

        return task_cls


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

    """
    Dataset information: 
    
    The pickup time interval (time between the earliest pickup time and the latest pickup time of a task) can be:
        - tight
        - loose
        - random

    The time window interval (time between tasks, i.e., the time between the latest delivery time of a task and the
    earliest start time of the next task) can be:
        - tight
        - loose
        - random

    The earliest pickup time of a task (ept) is: delivery_time_last_task + travel_time + time_window_interval,
    where the travel time is the estimated time to go from the delivery location of the previous task to the pickup
    location of the next task
    
    The latest pickup time (lpt) of a task is the ept + pickup time interval

    interval_type: Defines the pickup time interval and the time window interval

    An set of tasks consists of n consecutive tasks, where the time window interval between the tasks is defined as above.

    n_overlapping_sets: A dataset consists of one or more overlapping set of tasks
                        A dataset with non-overlapping-tw contains only one set
                        A dataset with overlapping-tw contains at least two sets

    The first task of all overlapping sets starts at the dataset's start_time

    The pickup and delivery pose names are randomly chosen from the pose_names

    task_creator: instance of class TaskCreator
    pose_creator: instance of class PoseCreator
    task_type: Class of the task in the dataset
    n_tasks: Number of tasks in the dataset
    n_overlapping_sets: Number of sets of overlapping tasks
    dataset_name: Name of the new dataset

    kwargs:

    interval_type (str): Defines the pickup time interval and the time window interval
                        'tight', 'loose' or 'random'

    pickup_time_lower_bound (int):  Lower bound of the pickup time interval
    pickup_time_upper_bound (int):  Upper bound of the pickup time interval

    time_window_lower_bound (int): Lower bound of the time window interval
    time_window_upper_bound (int): Upper bound of the time window interval

    n_overlapping_sets (int): Number of sets of consecutive tasks

    dataset_start_time (int): Earliest pickup time of the first task in each set of overlapping tasks

    map_sections (list): Sections of the map from where poses are chosen 

    """


def overlapping_time_windows(task_creator, pose_creator, task_type, n_tasks, n_overlapping_sets, dataset_name, **kwargs):
    """ Overlapping time windows dataset generator

    :return: dataset (a dictionary of n_tasks with overlapping time windows)
    """
    interval_type = kwargs.get('interval_type', 'random')
    pickup_time_lower_bound = kwargs.get('pickup_time_lower_bound')
    pickup_time_upper_bound = kwargs.get('pickup_time_upper_bound')
    time_window_lower_bound = kwargs.get('time_window_lower_bound')
    time_window_upper_bound = kwargs.get('time_window_upper_bound')
    dataset_start_time = kwargs.get('dataset_start_time')
    map_sections = kwargs.get('map_sections', ['square', 'street', 'faraway'])

    dataset_dict = get_metadata(dataset_name=dataset_name,
                                dataset_type='overlapping_tw',
                                task_type=task_type,
                                interval_type=interval_type,
                                pickup_time_lower_bound=pickup_time_lower_bound,
                                pickup_time_upper_bound=pickup_time_upper_bound,
                                time_window_lower_bound=time_window_lower_bound,
                                time_window_upper_bound=time_window_upper_bound,
                                dataset_start_time=dataset_start_time,
                                map_sections=map_sections)

    dataset_dict['tasks'] = dict()

    for i in range(0, n_overlapping_sets):
        n_tasks_set = int(n_tasks/n_overlapping_sets if n_tasks % n_overlapping_sets == 0
                          else n_tasks % n_overlapping_sets)

        tasks = get_tasks(task_creator, pose_creator, task_type, n_tasks_set, **kwargs)
        dataset_dict['tasks'].update(tasks)

    return dataset_dict


def non_overlapping_time_windows(task_creator, pose_creator, task_type, n_tasks, n_overlapping_sets, dataset_name, **kwargs):
    """ Non-overlapping time windows dataset generator

    :return: dataset (a dictionary of n_tasks with overlapping time windows)

    """
    interval_type = kwargs.get('interval_type', 'random')
    pickup_time_lower_bound = kwargs.get('pickup_time_lower_bound')
    pickup_time_upper_bound = kwargs.get('pickup_time_upper_bound')
    time_window_lower_bound = kwargs.get('time_window_lower_bound')
    time_window_upper_bound = kwargs.get('time_window_upper_bound')
    dataset_start_time = kwargs.get('dataset_start_time')
    map_sections = kwargs.get('map_sections', ['square', 'street', 'faraway'])

    dataset_dict = get_metadata(dataset_name=dataset_name,
                                dataset_type='non_overlapping_tw',
                                task_type=task_type,
                                interval_type=interval_type,
                                pickup_time_lower_bound=pickup_time_lower_bound,
                                pickup_time_upper_bound=pickup_time_upper_bound,
                                time_window_lower_bound=time_window_lower_bound,
                                time_window_upper_bound=time_window_upper_bound,
                                dataset_start_time=dataset_start_time,
                                map_sections=map_sections)

    dataset_dict['tasks'] = dict()

    tasks = get_tasks(task_creator, pose_creator, task_type, n_tasks, **kwargs)
    dataset_dict['tasks'].update(tasks)

    return dataset_dict


def get_tasks(task_creator, pose_creator, task_type, n_tasks_set, **kwargs):
    interval_type = kwargs.get('interval_type', 'random')
    pickup_time_lower_bound = kwargs.get('pickup_time_lower_bound')
    pickup_time_upper_bound = kwargs.get('pickup_time_upper_bound')
    time_window_lower_bound = kwargs.get('time_window_lower_bound')
    time_window_upper_bound = kwargs.get('time_window_upper_bound')
    dataset_start_time = kwargs.get('dataset_start_time')
    map_sections = kwargs.get('map_sections', ['square', 'street', 'faraway'])

    tasks = dict()
    last_task = None

    logging.debug("Getting a set of %s consecutive tasks", n_tasks_set)

    for j in range(0, n_tasks_set):
        time_window_interval = get_interval(interval_type, time_window_lower_bound, time_window_upper_bound)

        if last_task:
            logging.debug("Last task: %s", last_task.task_id)
            logging.debug("Delivery: %s", last_task.delivery_location)

            # The pickup pose of this task is the delivery of last task
            pickup_pose, delivery_pose = pose_creator.get_poses(map_sections, pickup_pose=last_task.delivery_location)

            # The finish (delivery) of last task is the latest pickup time plus the estimated time to go from
            # the pickup to the delivery location
            finish_last_task = last_task.latest_pickup_time + last_task.plan.estimated_duration

            # The travel path is the path between the delivery location of last task and the pickup of this task
            travel_path = get_plan(pose_creator, last_task.delivery_location, pickup_pose)

            # The travel time is the estimated time to go from the delivery of last task to the pickup of this task
            travel_time = travel_path.get('estimated_duration')
        else:
            # Randomly choose pickup and delivery poses
            pickup_pose, delivery_pose = pose_creator.get_poses(map_sections)
            finish_last_task = dataset_start_time
            travel_time = 0

        logging.debug("Finish time of last task: %s", finish_last_task)
        logging.debug("Travel time: %s", travel_time)
        logging.debug("Time window interval %s", time_window_interval)

        # Round to seconds
        ept = round(finish_last_task + travel_time + time_window_interval)
        lpt = round(ept +
                    get_interval(interval_type, pickup_time_lower_bound, pickup_time_upper_bound))

        plan = get_plan(pose_creator, pickup_pose, delivery_pose)

        _task_args = {'earliest_pickup_time': ept,
                      'latest_pickup_time': lpt,
                      'pickup_location': pickup_pose,
                      'delivery_location': delivery_pose,
                      'plan': plan}

        task = task_creator.create(task_type=task_type, **_task_args)
        last_task = task

        logging.debug("Task: %s", task.task_id)
        logging.debug("Earliest pickup time: %s", ept)
        logging.debug("Latest pickup time: %s", lpt)
        logging.debug("Pickup: %s", task.pickup_location)
        logging.debug("Delivery: %s", task.delivery_location)

        tasks[task.task_id] = task.to_dict()

    return tasks


def get_plan(pose_creator, pickup_pose, delivery_pose):
    path = pose_creator.get_path(pickup_pose, delivery_pose)
    mean, variance = pose_creator.get_estimated_duration(path)
    estimated_duration = round(mean + 2*(variance**0.5))
    return {'path': path, 'estimated_duration': estimated_duration}


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


def get_metadata(**kwargs):
    dataset_metadata = {key: value for (key, value) in kwargs.items()}
    dataset_metadata.update(dataset_id=generate_uuid())
    return dataset_metadata


task_factory = TaskFactory()
task_cls = getattr(import_module('dataset_lib.config.task'), 'Task')
task_factory.register_task_cls('task', task_cls)

dataset_factory = DatasetFactory()
dataset_factory.register_dataset_creator('overlapping', overlapping_time_windows)
dataset_factory.register_dataset_creator('non_overlapping', non_overlapping_time_windows)
