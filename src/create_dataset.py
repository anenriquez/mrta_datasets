from src.dataset_factory import DatasetCreator
from src.task_factory import initialize_task_factory
import argparse
from src.utils.datasets import load_yaml, store_as_yaml, store_as_csv


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('dataset_type', type=str, help='Dataset type',
                        choices=['overlapping_tw', 'non_overlapping_tw'])

    parser.add_argument('n_tasks', type=int, help='Number of tasks')

    parser.add_argument('dataset_name', type=str, help='Name of the dataset')

    parser.add_argument('--task_type', type=str, help='task type',
                        choices=['generic_task', 'ropod_task', 'task_request'],
                        default='generic_task')

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

    pose_names = load_yaml(args.poses_file).get('pose_names')

    dataset_creator = DatasetCreator()

    dataset = dataset_creator.create(args.task_type, args.dataset_type, args.n_tasks, args.dataset_name, pose_names,
                                     interval_type=args.interval_type,
                                     lower_bound=args.lower_bound,
                                     upper_bound=args.upper_bound)

    # Save in path datasets/dataset_type/task_type/interval_type

    path = '../datasets/' + args.dataset_type +\
           '/' + args.task_type+ '/' + \
           args.interval_type + '/'

    store_as_yaml(dataset, path)

    task_factory = initialize_task_factory()
    task_cls = task_factory.get_task_cls(args.task_type)
    store_as_csv(dataset, task_cls, path)

