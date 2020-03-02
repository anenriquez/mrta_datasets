import random

from dataset_lib.config.factories import dataset_factory
from dataset_lib.config.factories import task_factory
from planner.planner import Planner


class TaskCreator:

    def __init__(self, task_type):
        self.task_cls = task_factory.get_task_cls(task_type)

    def create(self, **kwargs):
        return self.task_cls(**kwargs)


class PoseCreator:

    def __init__(self, map_name):
        self.planner = Planner(map_name)

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

        return pickup_pose, delivery_pose

    def get_path(self, pickup_pose, delivery_pose):
        return self.planner.get_path(pickup_pose, delivery_pose)

    def get_estimated_duration(self, pickup_pose, delivery_pose):
        path = self.get_path(pickup_pose, delivery_pose)
        mean, variance = self.planner.get_estimated_duration(path)
        # Round to seconds
        estimated_duration = round(mean + 2*(variance**0.5))
        return estimated_duration

    def get_plan(self, pickup_pose, delivery_pose):
        path = self.get_path(pickup_pose, delivery_pose)
        estimated_duration = self.get_estimated_duration(pickup_pose, delivery_pose)
        return {'path': path, 'estimated_duration': estimated_duration}


class DatasetCreator:

    def __init__(self, task_type, map_name, dataset_meta):
        task_creator = TaskCreator(task_type)
        pose_creator = PoseCreator(map_name)
        dataset_creator_cls = dataset_factory.get_dataset_creator(dataset_meta.dataset_type)
        self.dataset_creator = dataset_creator_cls(task_creator, pose_creator, dataset_meta)

    def create(self, **kwargs):
        dataset = self.dataset_creator.create(**kwargs)
        return dataset
