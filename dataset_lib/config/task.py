from dataset_lib.utils.datasets import flatten_dict
from dataset_lib.utils.uuid import generate_uuid
from dataset_lib.utils.utils import AsDictionaryMixin


class Plan(AsDictionaryMixin):
    def __init__(self, path, estimated_duration):
        self.path = path
        self.estimated_duration = estimated_duration


class Task(AsDictionaryMixin):

    def __init__(self, earliest_pickup_time,
                 latest_pickup_time,
                 pickup_location,
                 delivery_location,
                 hard_constraints=True,
                 **kwargs):

        self.task_id = kwargs.get('task_id', generate_uuid())
        self.earliest_pickup_time = earliest_pickup_time
        self.latest_pickup_time = latest_pickup_time
        self.pickup_location = pickup_location
        self.delivery_location = delivery_location
        self.hard_constraints = hard_constraints
        self.plan = Plan(** kwargs.get('plan'))

    @staticmethod
    def to_csv(task_dict):
        """ Prepares dict to be written to a csv
        :return: dict
        """
        to_csv_dict = flatten_dict(task_dict)

        return to_csv_dict

