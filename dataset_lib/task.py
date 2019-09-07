from dataset_lib.utils.datasets import flatten_dict


class Task(object):

    def __init__(self,
                 task_id,
                 earliest_start_time,
                 latest_start_time,
                 start_location,
                 finish_location,
                 estimated_duration,
                 hard_constraints=True):

        self.task_id = task_id
        self.earliest_start_time = earliest_start_time
        self.latest_start_time = latest_start_time
        self.start_location = start_location
        self.finish_location = finish_location
        self.hard_constraints = hard_constraints
        self.estimated_duration = estimated_duration

    def to_dict(self):
        task_dict = dict()
        task_dict['task_id'] = self.task_id
        task_dict['earliest_start_time'] = self.earliest_start_time
        task_dict['latest_start_time'] = self.latest_start_time
        task_dict['start_location'] = self.start_location
        task_dict['finish_location'] = self.finish_location
        task_dict['hard_constraints'] = self.hard_constraints
        task_dict['estimated_duration'] = self.estimated_duration
        return task_dict

    @classmethod
    def from_dict(cls, task_dict):
        task_id = task_dict['task_id']
        earliest_start_time = task_dict['earliest_start_time']
        latest_start_time = task_dict['latest_start_time']
        start_location = task_dict['start_location']
        finish_location = task_dict['finish_location']
        hard_constraints = task_dict['hard_constraints']
        estimated_duration = task_dict['estimated_duration']
        task = cls(task_id, hard_constraints, earliest_start_time, latest_start_time,
                   start_location, finish_location, estimated_duration)
        return task

    @staticmethod
    def to_csv(task_dict):
        """ Prepares dict to be written to a csv
        :return: dict
        """
        to_csv_dict = flatten_dict(task_dict)

        return to_csv_dict

