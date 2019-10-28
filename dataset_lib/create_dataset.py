from dataset_lib.dataset_factory import DatasetCreator
from dataset_lib.task_factory import initialize_task_factory
import argparse
from dataset_lib.utils.datasets import load_yaml, store_as_yaml, store_as_csv


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

    parser.add_argument('--time_window_lower_bound', type=int, help='Time window interval lower bound (minutes)'
                        'The time window interval is the time between tasks, i.e., the time between'
                        'the latest finish time of a task and the earliest start time of the next',
                        default=1)

    parser.add_argument('--time_window_upper_bound', type=int, help='Time window interval upper bound (minutes)'
                        'The time window interval is the time between tasks, i.e., the time between'
                        'the latest finish time of a task and the earliest start time of the next',
                        default=3)

    parser.add_argument('--start_time_lower_bound', type=int, help='Start time interval lower bound (minutes)'
                        'The start time interval is the time between the earliest start time and the'
                        'latest start time of a task',
                        default=1)

    parser.add_argument('--start_time_upper_bound', type=int, help='Start time interval upper bound (minutes)'
                        'The start time interval is the time between the earliest start time and the'
                        'latest start time of a task',
                        default=2)

    parser.add_argument('--dataset_lower_bound', type=int, help='Earliest time of a task in the dataset (minutes)',
                        default=1)

    parser.add_argument('--dataset_upper_bound', type=int, help='Latest start time of task in the dataset (minutes)',
                        default=30)

    args = parser.parse_args()

    pose_names = load_yaml(args.poses_file).get('pose_names')

    dataset_creator = DatasetCreator()

    dataset = dataset_creator.create(args.task_type, args.dataset_type, args.n_tasks, args.dataset_name, pose_names,
                                     interval_type=args.interval_type,
                                     time_window_lower_bound=args.time_window_lower_bound,
                                     time_window_upper_bound=args.time_window_upper_bound,
                                     start_time_lower_bound=args.start_time_lower_bound,
                                     start_time_upper_bound=args.start_time_upper_bound,
                                     dataset_lower_bound=args.dataset_lower_bound,
                                     dataset_upper_bound=args.dataset_upper_bound)

    # Save in path datasets/dataset_type/task_type/interval_type

    path = '/datasets/' + args.dataset_type +\
           '/' + args.task_type + '/' + \
           args.interval_type + '/'

    store_as_yaml(dataset, path)

    task_factory = initialize_task_factory()
    task_cls = task_factory.get_task_cls(args.task_type)
    store_as_csv(dataset, task_cls, path)

