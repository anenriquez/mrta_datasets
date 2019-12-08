import numpy as np

from dataset_lib.utils.uuid import generate_uuid
from importlib import import_module
from importlib_resources import open_text


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


class PoseFactory:
    def __init__(self):
        self._map_files = {}

    def register_map_graph(self, map_name, map_json_file):
        self._map_files[map_name] = map_json_file

    def get_map(self, map_name):
        map_json_file = self._map_files.get(map_name)
        if not map_json_file:
            raise ValueError(map_name)
        return map_json_file


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


def overlapping_time_windows(task_creator, pose_creator, task_type, n_tasks, dataset_name, **kwargs):
    """ Overlapping time windows dataset generator

     The start time interval (time between the earliest start time and the latest
     start time of a task) can be:
        - tight
        - loose
        - random

    The earliest start time (est) of a task in the dataset is drawn from the interval
    (dataset_lower_bound, dataset_upper_bound)

    The latest_start_time (lst) of a task in the dataset is the est + start time interval

    The pickup and delivery pose names are randomly chosen from the pose_names

    :param task_creator: instance of class TaskCreator
    :param pose_creator: instance of class PoseCreator
    :param task_type: Class of the task in the dataset
    :param n_tasks: Number of tasks in the dataset
    :param dataset_name: Name of the new dataset

    :param kwargs:

    interval_type (str) :   'tight', 'loose' or 'random'
                            default: 'random'

    start_time_lower_bound (int):  default: 1 minute
    start_time_upper_bound (int):  default: 2 minutes

    dataset_lower_bound (int):  default: 1 minute
    dataset_upper_bound (int):  default: 30 minutes

    map_sections(list): default: ['square']

    :return: dataset (a dictionary of n_tasks with overlapping time windows)
    """
    interval_type = kwargs.get('interval_type', 'random')
    start_time_lower_bound = kwargs.get('start_time_lower_bound', 1)
    start_time_upper_bound = kwargs.get('start_time_upper_bound', 2)
    dataset_lower_bound = kwargs.get('dataset_lower_bound', 1)
    dataset_upper_bound = kwargs.get('dataset_upper_bound', 30)
    map_sections = kwargs.get('map_sections', ['square'])

    dataset_dict = get_metadata(dataset_name=dataset_name,
                                dataset_type='overlapping_tw',
                                task_type=task_type,
                                interval_type=interval_type,
                                start_time_lower_bound=start_time_lower_bound,
                                start_time_upper_bound=start_time_upper_bound,
                                dataset_lower_bound=dataset_lower_bound,
                                dataset_upper_bound=dataset_upper_bound,
                                map_sections=map_sections)

    dataset_dict['tasks'] = dict()

    for i in range(0, n_tasks):
        est = round(np.random.uniform(dataset_lower_bound, dataset_upper_bound), 2)
        lst = round(est +
                    get_interval(interval_type, start_time_lower_bound, start_time_upper_bound), 2)

        pickup_pose, delivery_pose = pose_creator.get_poses(map_sections)
        plan = get_plan(pose_creator, pickup_pose, delivery_pose)

        _task_args = {'earliest_pickup_time': est,
                      'latest_pickup_time': lst,
                      'pickup_location': pickup_pose,
                      'delivery_location': delivery_pose,
                      'plan': plan}

        task = task_creator.create(task_type=task_type, **_task_args)

        dataset_dict['tasks'][task.task_id] = task.to_dict()

    return dataset_dict


def non_overlapping_time_windows(task_creator, pose_creator, task_type, n_tasks, dataset_name, **kwargs):
    """ Non-overlapping time windows dataset generator

    The time window interval (time between tasks, i.e., the time between
    the latest finish time of a task and the earliest start time of the next
    task) can be:
        - tight
        - loose
        - random

    The earliest start time of a task (est) is the finish time of the last task
    plus the time window interval

    The start time interval (time between the earliest start time and the latest
     start time of a task) can be:
        - tight
        - loose
        - random

    The latest start time (lst) of a task in the dataset is the est + start time interval

    The duration of a task is estimated using the euclidean distance between the
    start and finish poses of the task (assuming a constant velocity of 1 m/s)

    The start and finish pose names are randomly chosen from the pose_names

    :param task_creator: instance of class TaskCreator
    :param pose_creator: instance of class PoseCreator
    :param task_type: Class of the task in the dataset
    :param n_tasks: Number of tasks in the dataset
    :param dataset_name: Name of the new dataset

    :param kwargs:

    interval_type (str) :   'tight', 'loose' or 'random'
                            default: 'random'

    time_window_lower_bound (int):  default: 1 minute
    time_window_upper_bound (int):  default: 3 minutes

    start_time_lower_bound (int):  default: 1 minute
    start_time_upper_bound (int):  default: 2 minutes

    map_sections(list): default: ['square']

    :return: dataset (a dictionary of n_tasks with overlapping time windows)

    """

    interval_type = kwargs.get('interval_type', 'random')
    time_window_lower_bound = kwargs.get('time_window_lower_bound', 1)
    time_window_upper_bound = kwargs.get('time_window_upper_bound', 3)
    start_time_lower_bound = kwargs.get('start_time_lower_bound', 1)
    start_time_upper_bound = kwargs.get('start_time_upper_bound', 2)
    map_sections = kwargs.get('map_sections', ['square'])

    dataset_dict = get_metadata(dataset_name=dataset_name,
                                dataset_type='non_overlapping_tw',
                                task_type=task_type,
                                interval_type=interval_type,
                                time_window_lower_bound=time_window_lower_bound,
                                time_window_upper_bound=time_window_upper_bound,
                                start_time_lower_bound=start_time_lower_bound,
                                start_time_upper_bound=start_time_upper_bound,
                                map_sections=map_sections)

    dataset_dict['tasks'] = dict()

    finish_last_task = time_window_lower_bound

    for i in range(0, n_tasks):

        time_window_interval = get_interval(interval_type, time_window_lower_bound, time_window_upper_bound)

        est = round(finish_last_task + time_window_interval, 2)
        lst = round(est +
                    get_interval(interval_type, start_time_lower_bound, start_time_upper_bound), 2)

        pickup_pose, delivery_pose = pose_creator.get_poses(map_sections)
        plan = get_plan(pose_creator, pickup_pose, delivery_pose)

        _task_args = {'earliest_pickup_time': est,
                      'latest_pickup_time': lst,
                      'pickup_location': pickup_pose,
                      'delivery_location': delivery_pose,
                      'plan': plan}

        task = task_creator.create(task_type=task_type, **_task_args)

        dataset_dict['tasks'][task.task_id] = task.to_dict()

        # Update finish last task
        finish_last_task = lst + plan.get('estimated_duration')

    return dataset_dict


def get_plan(pose_creator, pickup_pose, delivery_pose):
    path = pose_creator.get_path(pickup_pose, delivery_pose)
    mean, variance = pose_creator.get_estimated_duration(path)
    estimated_duration = mean + 2**(variance**0.5)
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

pose_factory = PoseFactory()
brsu_map = open_text('planner.maps', 'brsu.json').name
pose_factory.register_map_graph('brsu', brsu_map)

dataset_factory = DatasetFactory()
dataset_factory.register_dataset_creator('overlapping_tw', overlapping_time_windows)
dataset_factory.register_dataset_creator('non_overlapping_tw', non_overlapping_time_windows)
