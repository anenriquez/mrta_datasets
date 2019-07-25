from src.utils.uuid import generate_uuid
from src.utils.datasets import flatten_dict


class Task(object):

    def __init__(self, id='', earliest_start_time=-1, latest_start_time=-1,
                 estimated_duration = -1, start_pose_name='', finish_pose_name='',
                 hard_constraints = True):

        if not id:
            self.id = generate_uuid()
        else:
            self.id = id

        self.earliest_start_time = earliest_start_time
        self.latest_start_time = latest_start_time
        self.estimated_duration = estimated_duration
        self.start_pose_name = start_pose_name
        self.finish_pose_name = finish_pose_name
        self.hard_constraints = hard_constraints

    def to_dict(self):
        task_dict = dict()
        task_dict['id'] = self.id
        task_dict['earliest_start_time'] = self.earliest_start_time
        task_dict['latest_start_time'] = self.latest_start_time
        task_dict['estimated_duration'] = self.estimated_duration
        task_dict['start_pose_name'] = self.start_pose_name
        task_dict['finish_pose_name'] = self.finish_pose_name
        task_dict['hard_constraints'] = self.hard_constraints
        return task_dict

    @staticmethod
    def from_dict(task_dict):
        task = Task()
        task.id = task_dict['id']
        task.earliest_start_time = task_dict['earliest_start_time']
        task.latest_start_time = task_dict['latest_start_time']
        task.estimated_duration = task_dict['estimated_duration']
        task.start_pose_name = task_dict['start_pose_name']
        task.finish_pose_name = task_dict['finish_pose_name']
        task.hard_constraints = task_dict['hard_constraints']
        return task

    @staticmethod
    def to_csv(task_dict):
        """ Prepares dict to be written to a csv
        :return: dict
        """
        to_csv_dict = flatten_dict(task_dict)

        return to_csv_dict
