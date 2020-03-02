import argparse
import logging

import yaml
from dataset_lib.config.creators import DatasetCreator
from dataset_lib.config.factories import DatasetMeta, Interval
from dataset_lib.utils.datasets import get_dataset_name

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

    parser.add_argument('--task_type', type=str, help='task type', choices=['task'], default='task')

    parser.add_argument('--map_name', type=str, help='Name of the map to get poses from', default='brsu')

    parser.add_argument('--map_sections', type=list, help='Name of sections in the map to take goal poses from',
                        default=['square', 'street', 'faraway'])

    args = parser.parse_args()

    dataset_name = get_dataset_name(args.n_overlapping_sets, args.interval_type)
    dataset_type = dataset_name.split('_')[0]

    print("Dataset name: ", dataset_name)
    print("Dataset type: ", dataset_type)

    pickup_time_interval = Interval(args.interval_type, args.pickup_time_lower_bound, args.pickup_time_upper_bound)
    time_window_interval = Interval(args.interval_type, args.time_window_lower_bound, args.time_window_upper_bound)

    dataset_meta = DatasetMeta(dataset_name, dataset_type, args.dataset_start_time, pickup_time_interval,
                               time_window_interval, args.map_sections)

    dataset_creator = DatasetCreator(args.task_type, args.map_name, dataset_meta)

    logging.basicConfig(level=logging.DEBUG)

    dataset, tasks = dataset_creator.create(n_tasks=args.n_tasks, n_overlapping_sets=args.n_overlapping_sets)

    dataset_file = 'datasets/' + dataset_name + '.yaml'

    with open(dataset_file, 'w') as outfile:
        yaml.safe_dump(dataset, outfile, default_flow_style=False)
