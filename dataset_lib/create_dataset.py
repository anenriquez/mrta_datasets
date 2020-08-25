import argparse
import logging

from dataset_lib.config.creators import DatasetCreator
from dataset_lib.config.factories import DatasetMeta, Interval
from dataset_lib.utils.datasets import get_dataset_name, store_as_yaml

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('n_tasks', type=int, help='Number of tasks')

    parser.add_argument('n_overlapping_sets', type=int, help='Number of sets of consecutive tasks'
                        'A dataset with non-overlapping-tw contains only one set, '
                        'A dataset with overlapping-tw contains at least two sets')

    parser.add_argument('interval_type', type=str, help='Pickup time interval and time window interval type',
                        choices=['tight', 'loose', 'random'])

    parser.add_argument('--pickup_time_lower_bound', type=int, help='Pickup time interval lower bound (seconds) '
                        'The pickup time interval is the time between the earliest and the latest pickup time',
                        default=60)

    parser.add_argument('--pickup_time_upper_bound', type=int, help='Pickup time interval upper bound (seconds)'
                        'The pickup time interval is the time between the earliest and the latest pickup time',
                        default=300)

    parser.add_argument('--time_window_lower_bound', type=int, help='Time window interval lower bound (seconds)'
                        'The time window interval is the time between tasks, i.e., the time between'
                        'the latest finish time of a task and the earliest start time of the next',
                        default=60)

    parser.add_argument('--time_window_upper_bound', type=int, help='Time window interval upper bound (seconds)'
                        'The time window interval is the time between tasks, i.e., the time between'
                        'the latest finish time of a task and the earliest start time of the next',
                        default=300)

    parser.add_argument('--dataset_start_time', type=int, help='Dataset start time', default=1800)

    parser.add_argument('--task_type', type=str, help='task type', choices=['transportation'], default='transportation')

    parser.add_argument('--map_name', type=str, help='Name of the map to get poses from', default='brsu')

    parser.add_argument('--map_sections', type=list, help='Name of sections in the map to take goal poses from',
                        default=['square', 'street'])

    parser.add_argument('--min_duration', type=int, help='Minimum duration (seconds) between pickup and delivery',
                        default=30)

    parser.add_argument('--max_duration', type=int, help='Maximum duration (seconds) between pickup and delivery',
                        default=120)

    args = parser.parse_args()

    dataset_name = get_dataset_name(args.n_tasks, args.n_overlapping_sets, args.interval_type)
    dataset_type = dataset_name.split('_')[0]
    duration_range = list(range(args.min_duration, args.max_duration))

    print("Dataset name: ", dataset_name)
    print("Dataset type: ", dataset_type)

    pickup_time_interval = Interval(args.interval_type, args.pickup_time_lower_bound, args.pickup_time_upper_bound)
    time_window_interval = Interval(args.interval_type, args.time_window_lower_bound, args.time_window_upper_bound)

    meta_info = {'dataset_name': dataset_name,
                 'dataset_type': dataset_type,
                 'start_time': args.dataset_start_time,
                 'pickup_time_interval': pickup_time_interval,
                 'time_window_interval': time_window_interval,
                 'map_sections': args.map_sections,
                 'task_type': args.task_type
                 }

    dataset_meta = DatasetMeta(**meta_info)

    dataset_creator = DatasetCreator(args.task_type, args.map_name, dataset_meta)

    logging.basicConfig(level=logging.DEBUG)

    dataset, tasks = dataset_creator.create(n_tasks=args.n_tasks, n_overlapping_sets=args.n_overlapping_sets,
                                            duration_range=duration_range)

    file_path = 'datasets/' + args.map_name

    store_as_yaml(dataset, dataset_name, file_path)

