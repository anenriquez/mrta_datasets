from src.dataset_factory import DatasetCreator
from src.task_factory import TaskFactory
import argparse
import yaml
from ropod.structs.task import Task as RopodTask
from src.task import Task as GenericTask
GenericTask.__name__ = 'GenericTask'
RopodTask.__name__ = 'RopodTask'


def load_file(file):
    """ Reads a yaml file and returns a dictionary with its contents

    :param file: file to load
    :return: data as dict()
    """
    file_handle = open(file, 'r')
    data = yaml.safe_load(file_handle)
    file_handle.close()
    return data


def get_task_cls(task_cls_name):
    task_factory = TaskFactory()
    task_factory.register_task_cls(GenericTask.__name__, GenericTask)
    task_factory.register_task_cls(RopodTask.__name__, RopodTask)

    return task_factory.get_task_cls(task_cls_name)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('dataset_type', type=str, help='Dataset type',
                        choices=['overlapping_tw', 'non_overlapping_tw'])

    parser.add_argument('n_tasks', type=int, help='Number of tasks')

    parser.add_argument('dataset_name', type=str, help='Name of the dataset')

    parser.add_argument('--task_cls_name', type=str, help='Task class name',
                        choices=['GenericTask', 'RopodTask'],
                        default='GenericTask')

    parser.add_argument('--poses_file', type=str, help='Path to the config file',
                        default='../poses/brsu_c069_lab.yaml')

    parser.add_argument('--interval_type', type=str,
                        help='Start time interval for overlapping tw'
                        'or time window interval for non_overlapping_tw',
                        choices=['tight', 'loose', 'random'], default='random')

    parser.add_argument('--lower_bound', type=int, help='Lower interval bound (seconds)',
                        default=60)

    parser.add_argument('--upper_bound', type=int, help='Upper interval bound (seconds)',
                        default=300)

    args = parser.parse_args()

    task_cls = get_task_cls(args.task_cls_name)

    pose_names = load_file(args.poses_file).get('pose_names')

    dataset_creator = DatasetCreator(args.dataset_type)

    dataset = dataset_creator.create(task_cls, args.n_tasks, args.dataset_name, pose_names,
                                     interval_type=args.interval_type,
                                     lower_bound= args.lower_bound,
                                     upper_bound=args.upper_bound)

    print(dataset)

    # Save in path datasets/dataset_type/task_type/interval_type

    path = '../datasets/' + args.dataset_type +\
           '/' + args.task_cls_name.lower() + '/' + \
           args.interval_type + '/'

    dataset_creator.store_as_yaml(dataset, path)

