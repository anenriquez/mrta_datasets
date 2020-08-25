from dataset_lib.utils.datasets import flatten_dict
from dataset_lib.utils.uuid import generate_uuid
from dataset_lib.utils.utils import AsDictionaryMixin


class Plan(AsDictionaryMixin):
    def __init__(self, path, estimated_duration):
        self.path = path
        self.estimated_duration = estimated_duration


class Transportation(AsDictionaryMixin):

    def __init__(self, pickup_location, delivery_location, hard_constraints=True, **kwargs):

        self.request_id = kwargs.get('task_id', generate_uuid())
        self.pickup_location = pickup_location
        self.delivery_location = delivery_location
        self.hard_constraints = hard_constraints
        self.earliest_pickup_time = kwargs.get('earliest_pickup_time')
        self.latest_pickup_time = kwargs.get('latest_pickup_time')
        self.plan = Plan(** kwargs.get('plan'))
        self.set_number = kwargs.get('set_number')

    @staticmethod
    def to_csv(task_dict):
        """ Prepares dict to be written to a csv
        :return: dict
        """
        to_csv_dict = flatten_dict(task_dict)

        return to_csv_dict

