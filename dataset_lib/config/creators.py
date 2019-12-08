import random

from planner.planner import Planner

from dataset_lib.config.factories import dataset_factory
from dataset_lib.config.factories import pose_factory
from dataset_lib.config.factories import task_factory


class TaskCreator:

    def __init__(self):
        self.task_factory = task_factory

    def create(self, task_type, **kwargs):
        task_cls = self.task_factory.get_task_cls(task_type)
        return task_cls(**kwargs)


class PoseCreator:

    def __init__(self, map_name):
        self.pose_factory = pose_factory
        self.planner = self.get_planner(map_name)

    def get_planner(self, map_name):
        planner = Planner()
        map_json_file = self.pose_factory.get_map(map_name)
        planner.load_map(map_json_file)
        return planner

    def get_poses(self, map_sections):
        goals = list()
        for section in map_sections:
            for pose in self.planner.map_graph.graph['goals'][section]:
                goals.append(pose)

        available_poses = [pose for pose in list(self.planner.map_graph.nodes())
                           if pose in goals]

        pickup_pose = random.choice(available_poses)
        available_poses.remove(pickup_pose)
        delivery_pose = random.choice(available_poses)

        if self.planner.map_graph.has_edge(pickup_pose, delivery_pose):
            self.get_poses(map_sections)

        return pickup_pose, delivery_pose

    def get_path(self, pickup_pose, delivery_pose):
        return self.planner.get_path(pickup_pose, delivery_pose)

    def get_estimated_duration(self, path):
        mean, variance = self.planner.get_estimated_duration(path)
        return mean, variance


class DatasetCreator:

    def __init__(self, map_name):
        self.task_creator = TaskCreator()
        self.pose_creator = PoseCreator(map_name)
        self.dataset_factory = dataset_factory

    def create(self, task_type, dataset_type, n_tasks, dataset_name, **kwargs):
        dataset_creator = self.dataset_factory.get_dataset_creator(dataset_type)
        dataset = dataset_creator(self.task_creator, self.pose_creator, task_type, n_tasks, dataset_name, **kwargs)

        return dataset
