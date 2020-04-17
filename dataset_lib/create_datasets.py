import argparse
import logging

import yaml
from dataset_lib.config.creators import DatasetCreator
from dataset_lib.config.factories import Interval, DatasetMeta
from dataset_lib.utils.datasets import get_dataset_name


def create_datasets(n_tasks, n_overlapping_sets, dataset_start_time, pickup_time_boundaries, time_window_boundaries,
                    duration_range, **kwargs):
    """
    Creates a dataset with the same tasks for each interval type
    """
    map_name = kwargs.get('map_name', 'brsu')
    map_sections = kwargs.get('map_sections', ['square', 'street', 'faraway'])
    task_type = kwargs.get('task_type', 'task')

    time_window_interval_types = ['tight', 'loose', 'random']

    # Use the same pickup interval for all time window interval types
    pickup_time_interval = Interval('tight', pickup_time_boundaries[0], pickup_time_boundaries[1])

    tasks = dict()

    for interval_type in time_window_interval_types:
        print("TW Interval type: ", interval_type)
        dataset_name = get_dataset_name(n_tasks, n_overlapping_sets, interval_type)
        dataset_type = dataset_name.split('_')[0]

        print("dataset_name: ", dataset_name)
        print("dataset_type: ", dataset_type)

        time_window_interval = Interval(interval_type, time_window_boundaries[0], time_window_boundaries[1])

        dataset_meta = DatasetMeta(dataset_name, dataset_type, dataset_start_time, pickup_time_interval,
                                   time_window_interval, map_sections)

        dataset_creator = DatasetCreator(task_type, map_name, dataset_meta)

        if not tasks:
            dataset, tasks = dataset_creator.create(n_tasks=n_tasks, n_overlapping_sets=n_overlapping_sets,
                                                    duration_range=duration_range)
        else:
            dataset, tasks = dataset_creator.create(n_tasks=n_tasks, n_overlapping_sets=n_overlapping_sets, tasks=tasks,
                                                    duration_range=duration_range)

        dataset_file = 'datasets/' + dataset_name + '.yaml'

        with open(dataset_file, 'w') as outfile:
            yaml.safe_dump(dataset, outfile, default_flow_style=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('n_tasks', type=int, help='Number of tasks')

    parser.add_argument('n_overlapping_sets', type=int, help='Number of sets of consecutive tasks'
                        'A dataset with non-overlapping-tw contains only one set, '
                        'A dataset with overlapping-tw contains at least two sets')

    parser.add_argument('--dataset_start_time', type=int, help='Dataset start time (seconds after time 0)', default=2700)

    parser.add_argument('--pickup_time_lower_bound', type=int, help='Pickup time interval lower bound (seconds) '
                        'The pickup time interval is the time between the earliest and the latest pickup time',
                        default=30)

    parser.add_argument('--pickup_time_upper_bound', type=int, help='Pickup time interval upper bound (seconds)'
                                                                    'The pickup time interval is the time between the earliest and the latest pickup time',
                        default=60)

    parser.add_argument('--time_window_lower_bound', type=int, help='Time window interval lower bound (seconds)'
                        'The time window interval is the time between tasks, i.e., the time between'
                        'the latest finish time of a task and the earliest start time of the next',
                        default=30)

    parser.add_argument('--time_window_upper_bound', type=int, help='Time window interval upper bound (seconds)'
                        'The time window interval is the time between tasks, i.e., the time between'
                        'the latest finish time of a task and the earliest start time of the next',
                        default=120)

    parser.add_argument('--min_duration', type=int, help='Minimum duration (seconds) between pickup and delivery',
                        default=30)

    parser.add_argument('--max_duration', type=int, help='Maximum duration (seconds) between pickup and delivery',
                        default=120)

    args = parser.parse_args()

    duration_range = list(range(args.min_duration, args.max_duration+1))

    pickup_time_boundaries = [args.pickup_time_lower_bound, args.pickup_time_upper_bound]

    time_window_boundaries = [args.time_window_lower_bound, args.time_window_upper_bound]

    logging.basicConfig(level=logging.DEBUG)

    create_datasets(args.n_tasks, args.n_overlapping_sets, args.dataset_start_time, pickup_time_boundaries,
                    time_window_boundaries, duration_range)
