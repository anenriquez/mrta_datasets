from ropod.structs.task import Task as RopodTask
from src.task import Task as GenericTask
from src.utils.uuid import generate_uuid
from ropod.structs.area import Area

GenericTask.__name__ = 'GenericTask'
RopodTask.__name__ = 'RopodTask'


class TaskFactory(object):
    def __init__(self):
        self._task_creators = {}
        self._task_csv_loaders = {}
        self._task_cls = {}

    def register_task_creator(self, task_name, task_creator):
        self._task_creators[task_name] = task_creator

    def get_task_creator(self, task_name):
        task_creator = self._task_creators.get(task_name)
        if not task_creator:
            raise ValueError(task_name)
        return task_creator

    def register_task_csv_loader(self, task_name, task_csv_loader):
        self._task_csv_loaders[task_name] = task_csv_loader

    def get_task_csv_loader(self, task_name):
        task_csv_loader = self._task_csv_loaders.get(task_name)
        if not task_csv_loader:
            raise ValueError(task_name)
        return task_csv_loader

    def register_task_cls(self, task_name, task_cls):
        self._task_cls[task_name] = task_cls

    def get_task_cls(self, task_name):
        task_cls = self._task_cls.get(task_name)
        if not task_cls:
            raise ValueError(task_name)

        return task_cls


def generic_task_creator(task_cls, **kwargs):
    task = task_cls(id=generate_uuid(), **kwargs)

    return task


def ropod_task_creator(task_cls, **kwargs):
    pickup_pose = kwargs.get('start_pose_name', Area())
    delivery_pose = kwargs.get('finish_pose_name', Area())
    earliest_start_time = kwargs.get('earliest_start_time', -1)
    latest_start_time = kwargs.get('latest_start_time', -1)

    task = task_cls()
    task.pickup_pose.name = pickup_pose
    task.delivery_pose.name = delivery_pose
    task.earliest_start_time = earliest_start_time
    task.latest_start_time = latest_start_time

    return task


def generic_task_csv_loader(task_cls, task_csv):
    id = task_csv['id']

    _task_args = {'earliest_start_time': task_csv['earliest_start_time'],
                  'latest_start_time': task_csv['latest_start_time'],
                  'start_pose_name': task_csv['start_pose_name'],
                  'finish_pose_name': task_csv['finish_pose_name'],
                  'hard_constraints': task_csv['hard_constraints']
                  }

    task = task_cls(id, **_task_args)
    return task


def ropod_task_csv_loader(task_cls, task_csv):

    task = task_cls()

    task.id = task_csv['id']
    task.pickup_pose.name = task_csv['pickup_pose_name']
    task.delivery_pose.name = task_csv['delivery_pose_name']
    task.earliest_start_time = task_csv['earliest_start_time']
    task.latest_start_time = task_csv['latest_start_time']
    task.hard_constraints = task_csv['hard_constraints']

    return task


def initialize_factory():
    task_factory = TaskFactory()

    task_factory.register_task_creator(GenericTask.__name__,
                                       generic_task_creator)

    task_factory.register_task_csv_loader(GenericTask.__name__,
                                          generic_task_csv_loader)

    task_factory.register_task_cls(GenericTask.__name__, GenericTask)

    task_factory.register_task_creator(RopodTask.__name__,
                                       ropod_task_creator)

    task_factory.register_task_csv_loader(RopodTask.__name__,
                                          ropod_task_csv_loader)

    task_factory.register_task_cls(RopodTask.__name__, RopodTask)

    return task_factory


class TaskCreator(object):
    def __init__(self, task_cls):
        task_factory = initialize_factory()

        self.task_cls = task_cls
        self.task_generator = task_factory.get_task_creator(task_cls.__name__)

    def create(self, **kwargs):
        new_task = self.task_generator(self.task_cls, **kwargs)
        return new_task

    def get_task_cls_name(self):
        return self.task_cls.__name__


class TaskLoader(object):
    def __init__(self, task_cls):
        task_factory = initialize_factory()
        self.task_csv_loader = task_factory.get_task_csv_loader(task_cls.__name__)
        self.task_cls = task_cls

    def load_csv(self, task_csv):
        task = self.task_csv_loader(self.task_cls, task_csv)
        return task
