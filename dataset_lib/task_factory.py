from dataset_lib.utils.uuid import generate_uuid
from importlib import import_module


class TaskFactory(object):
    def __init__(self):
        self._task_creators = {}
        self._task_csv_loaders = {}
        self._task_cls = {}

    def register_task_creator(self, task_type, task_creator):
        self._task_creators[task_type] = task_creator

    def get_task_creator(self, task_type):
        task_creator = self._task_creators.get(task_type)
        if not task_creator:
            raise ValueError(task_type)
        return task_creator

    def register_task_csv_loader(self, task_type, task_csv_loader):
        self._task_csv_loaders[task_type] = task_csv_loader

    def get_task_csv_loader(self, task_type):
        task_csv_loader = self._task_csv_loaders.get(task_type)
        if not task_csv_loader:
            raise ValueError(task_type)
        return task_csv_loader

    def register_task_cls(self, task_type, task_cls):
        self._task_cls[task_type] = task_cls

    def get_task_cls(self, task_type):
        task_cls = self._task_cls.get(task_type)
        if not task_cls:
            raise ValueError(task_type)

        return task_cls


def generic_task_creator(task_cls, **kwargs):
    # task = task_cls(id=generate_uuid(), **kwargs)
    task = task_cls(task_id=generate_uuid(), **kwargs)

    return task


def ropod_task_creator(task_cls, **kwargs):

    area_cls = getattr(import_module('ropod.structs.area'), 'Area')

    pickup_pose = kwargs.get('start_pose_name', area_cls())
    delivery_pose = kwargs.get('finish_pose_name', area_cls())
    earliest_start_time = kwargs.get('earliest_start_time', -1)
    latest_start_time = kwargs.get('latest_start_time', -1)
    estimated_duration = kwargs.get('estimated_duration', -1)

    task = task_cls()
    task.pickup_pose.name = pickup_pose
    task.delivery_pose.name = delivery_pose
    task.earliest_start_time = earliest_start_time
    task.latest_start_time = latest_start_time
    task.estimated_duration = estimated_duration

    return task


def task_request_creator(task_cls, **kwargs):

    area_cls = getattr(import_module('ropod.structs.area'), 'Area')

    pickup_pose = kwargs.get('start_pose_name', area_cls())
    delivery_pose = kwargs.get('finish_pose_name', area_cls())
    earliest_start_time = kwargs.get('earliest_start_time', -1)
    latest_start_time = kwargs.get('latest_start_time', -1)

    task = task_cls()
    task.pickup_pose.name = pickup_pose
    task.delivery_pose.name = delivery_pose
    task.earliest_start_time = earliest_start_time
    task.latest_start_time = latest_start_time

    return task


def generic_task_csv_loader(task_cls, task_csv):
    task_id = task_csv['task_id']

    _task_args = {'earliest_start_time': float(task_csv['earliest_start_time']),
                  'latest_start_time': float(task_csv['latest_start_time']),
                  'estimated_duration': float(task_csv['estimated_duration']),
                  'start_location': task_csv['start_location'],
                  'finish_location': task_csv['finish_location'],
                  'hard_constraints': task_csv['hard_constraints']
                  }

    task = task_cls(task_id, **_task_args)
    return task


def ropod_task_csv_loader(task_cls, task_csv):

    task = task_cls()

    task.id = task_csv['id']
    task.pickup_pose.name = task_csv['pickup_pose_name']
    task.delivery_pose.name = task_csv['delivery_pose_name']
    task.earliest_start_time = float(task_csv['earliest_start_time'])
    task.latest_start_time = float(task_csv['latest_start_time'])
    task.estimated_duration = float(task_csv['estimated_duration'])
    task.hard_constraints = task_csv['hard_constraints']

    return task


def task_request_csv_loader(task_cls, task_csv):

    task = task_cls()

    task.id = task_csv['id']
    task.pickup_pose.name = task_csv['pickup_pose_name']
    task.delivery_pose.name = task_csv['delivery_pose_name']
    task.earliest_start_time = float(task_csv['earliest_start_time'])
    task.latest_start_time = float(task_csv['latest_start_time'])

    return task


def initialize_task_factory():
    task_factory = TaskFactory()

    ropod_task_cls = getattr(import_module('ropod.structs.task'), 'Task')

    task_factory.register_task_cls('ropod_task', ropod_task_cls)
    task_factory.register_task_creator('ropod_task', ropod_task_creator)
    task_factory.register_task_csv_loader('ropod_task', ropod_task_csv_loader)

    generic_task_cls = getattr(import_module('dataset_lib.task'), 'Task')

    task_factory.register_task_cls('generic_task', generic_task_cls)
    task_factory.register_task_creator('generic_task', generic_task_creator)
    task_factory.register_task_csv_loader('generic_task', generic_task_csv_loader)

    task_request_cls = getattr(import_module('ropod.structs.task'), 'TaskRequest')

    task_factory.register_task_cls('task_request', task_request_cls)
    task_factory.register_task_creator('task_request', task_request_creator)
    task_factory.register_task_csv_loader('task_request', task_request_csv_loader)

    return task_factory


class TaskCreator(object):

    def __init__(self):
        self.task_factory = initialize_task_factory()

    def create(self, task_type, **kwargs):
        task_creator = self.task_factory.get_task_creator(task_type)
        task_cls = self.task_factory.get_task_cls(task_type)

        new_task = task_creator(task_cls, **kwargs)
        return new_task


class TaskLoader(object):

    def __init__(self):
        self.task_factory = initialize_task_factory()

    def load_csv(self, task_type, task_csv):
        task_csv_loader = self.task_factory.get_task_csv_loader(task_type)
        task_cls = self.task_factory.get_task_cls(task_type)
        task = task_csv_loader(task_cls, task_csv)
        return task
