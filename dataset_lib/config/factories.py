import logging
from importlib import import_module

import numpy as np
from dataset_lib.utils.utils import AsDictionaryMixin


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


class DatasetMeta(AsDictionaryMixin):
    """
    Dataset information:

    The pickup_time_interval (time between the earliest pickup time and the latest pickup time of a task) can be:
        - tight
        - loose
        - random

    The time_window_interval (time between tasks, i.e., the time between the latest delivery time of a task and the
    earliest start time of the next task) can be:
        - tight
        - loose
        - random

    The earliest pickup time of a task (ept) is: delivery_time_last_task + travel_time + time_window_interval,
    where the travel time is the estimated time to go from the delivery location of the previous task to the pickup
    location of the next task

    The latest pickup time (lpt) of a task is the ept + pickup time interval

    interval_type: Defines the pickup_time_interval and the time_window_interval

    A set of tasks consists of n consecutive tasks, where the time window interval between the tasks is defined as above

    n_overlapping_sets: A dataset consists of one or more overlapping set of tasks

    A dataset with non-overlapping-time-windows contains only one set
    A dataset with overlapping-time-windows contains at least two sets

    start_time (int): Used to compute the earliest pickup time of the first task in each set of overlapping tasks
    The first task of all overlapping sets starts at the dataset's start_time + pickup_time_interval

    dataset_name: Name of the dataset

    map_sections (list): Sections of the map from where poses are chosen

    The pickup and delivery pose names are randomly chosen from the pose_names

    """

    def __init__(self, **kwargs):
        self.dataset_name = kwargs.get("dataset_name")
        self.dataset_type = kwargs.get("dataset_type")
        self.start_time = kwargs.get("start_time")
        self.pickup_time_interval = kwargs.get("pickup_time_interval")
        self.time_window_interval = kwargs.get("time_window_interval")
        self.map_sections = kwargs.get("map_sections")
        self.task_type = kwargs.get("task_type")


class Interval(AsDictionaryMixin):
    def __init__(self, interval_type, lower_bound, upper_bound):
        self.interval_type = interval_type
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def __str__(self):
        return "{}: [{}, {}]".format(self.interval_type, self.lower_bound, self.upper_bound)

    def __call__(self, *args, **kwargs):
        if self.interval_type == 'tight':
            interval = self.lower_bound
        elif self.interval_type == 'loose':
            interval = self.upper_bound
        elif self.interval_type == 'random':
            interval = np.random.uniform(self.lower_bound, self.upper_bound)
        else:
            raise ValueError(self.interval_type)
        # Round to seconds
        return round(interval)


class OverlappingTW:
    def __init__(self, task_creator, pose_creator, dataset_meta):
        """ Creates datasets with overlapping time windows
        """
        self.task_creator = task_creator
        self.pose_creator = pose_creator
        self.dataset_meta = dataset_meta

    def create(self, n_tasks, n_overlapping_sets, **kwargs):
        dataset = self.dataset_meta.to_dict()
        dataset['tasks'] = dict()
        tasks = kwargs.get("tasks")
        duration_range = kwargs.get('duration_range')

        if tasks is None:
            tasks = dict()

            n_tasks_sets = [int(n_tasks / n_overlapping_sets)] * n_overlapping_sets
            if n_tasks % n_overlapping_sets != 0:
                n_tasks_sets.append(n_tasks % n_overlapping_sets)

            map_sections = self.dataset_meta.map_sections * round(len(n_tasks_sets)/len(self.dataset_meta.map_sections))

            # Use a map section per tasks_set
            for i, (n_tasks_set, map_section) in enumerate(zip(n_tasks_sets, map_sections)):
                tasks_set = get_tasks_set(self.task_creator, self.pose_creator, duration_range, n_tasks_set, [map_section], i)
                tasks_set = order_by_estimated_durations(tasks_set)
                tasks[i] = tasks_set

        for i, tasks_set in tasks.items():
            tasks_set = add_constraints(tasks_set, self.dataset_meta.pickup_time_interval,
                                        self.dataset_meta.time_window_interval, self.dataset_meta.start_time,
                                        self.pose_creator)
            for task in tasks_set:
                dataset["tasks"][task.request_id] = task.to_dict()

        return dataset, tasks


class NonOverlappingTW:
    def __init__(self, task_creator, pose_creator, dataset_meta):
        """ Creates datasets with non overlapping time windows
        """
        self.task_creator = task_creator
        self.pose_creator = pose_creator
        self.dataset_meta = dataset_meta

    def create(self, n_tasks, **kwargs):
        dataset = self.dataset_meta.to_dict()
        dataset['tasks'] = dict()
        tasks = kwargs.get("tasks")
        duration_range = kwargs.get('duration_range')

        if tasks is None:
            tasks = get_tasks_set(self.task_creator, self.pose_creator, duration_range, n_tasks, self.dataset_meta.map_sections)
            tasks = order_by_estimated_durations(tasks)

        tasks = add_constraints(tasks, self.dataset_meta.pickup_time_interval, self.dataset_meta.pickup_time_interval,
                                self.dataset_meta.start_time, self.pose_creator)

        for task in tasks:
            dataset["tasks"][task.request_id] = task.to_dict()

        return dataset, tasks


def get_tasks_set(task_creator, pose_creator, duration_range, n_tasks_set, map_sections, set_number=1):
    """ Returns tasks without temporal information
    """
    tasks = list()

    logging.debug("Getting a set of %s consecutive tasks using map_sections %s", n_tasks_set, map_sections)

    for j in range(0, n_tasks_set):
        pickup_pose, delivery_pose = pose_creator.get_poses(map_sections, duration_range)
        plan = pose_creator.get_plan(pickup_pose, delivery_pose)

        _task_args = {'pickup_location': pickup_pose,
                      'delivery_location': delivery_pose,
                      'plan': plan,
                      'set_number': set_number
                      }

        task = task_creator.create(**_task_args)
        print("task: ", task)

        tasks.append(task)

    return tasks


def order_by_estimated_durations(tasks):
    return sorted(tasks, key=lambda task: task.plan.estimated_duration)


def add_constraints(tasks, pickup_time_interval, time_window_interval, dataset_start_time, pose_creator):
    """
    Adds temporal constraints to a set of consecutive tasks
    """
    print("dataset start_time: ", dataset_start_time)

    for i, task in enumerate(tasks):
        if i > 0:
            last_task = tasks[i-1]

            # The finish (delivery) of last task is the latest pickup time plus the estimated time to go from
            # the pickup to the delivery location
            finish_last_task = last_task.latest_pickup_time + last_task.plan.estimated_duration

            # The travel path is the path between the delivery location of last task and the pickup of this task
            travel_path = pose_creator.get_plan(last_task.delivery_location, task.pickup_location)

            # The travel time is the estimated time to go from the delivery of last task to the pickup of this task
            travel_time = travel_path.get('estimated_duration')

            task.earliest_pickup_time = finish_last_task + travel_time + time_window_interval()

        else:
            task.earliest_pickup_time = dataset_start_time

        task.latest_pickup_time = task.earliest_pickup_time + pickup_time_interval()

        logging.debug("Task %s earliest pickup time: %s", task.request_id, task.earliest_pickup_time)
        logging.debug("Task %s latest pickup time: %s", task.request_id, task.latest_pickup_time)

    return tasks


task_factory = TaskFactory()
task_cls = getattr(import_module('dataset_lib.config.request'), 'Transportation')
task_factory.register_task_cls('transportation', task_cls)

dataset_factory = DatasetFactory()
dataset_factory.register_dataset_creator('overlapping', OverlappingTW)
dataset_factory.register_dataset_creator('nonoverlapping', NonOverlappingTW)
