import argparse
import logging

import yaml
from dataset_lib.config.creators import DatasetCreator
from dataset_lib.config.factories import Interval, DatasetMeta
from dataset_lib.utils.datasets import get_dataset_name


def create_datasets(n_tasks, n_overlapping_sets, dataset_start_time, lower_bound, upper_bound, **kwargs):
    """
    Creates a dataset with the same tasks for each interval type
    """
    map_name = kwargs.get('map_name', 'brsu')
    map_sections = kwargs.get('map_sections', ['square', 'street', 'faraway'])
    task_type = kwargs.get('task_type', 'task')

    interval_types = ['tight', 'loose', 'random']
    tasks = dict()

    for interval_type in interval_types:
        print("Interval type: ", interval_type)
        dataset_name = get_dataset_name(n_overlapping_sets, interval_type)
        dataset_type = dataset_name.split('_')[0]

        print("dataset_name: ", dataset_name)
        print("dataset_type: ", dataset_type)

        pickup_time_interval = Interval(interval_type, lower_bound, upper_bound)
        time_window_interval = Interval(interval_type, lower_bound, upper_bound)

        dataset_meta = DatasetMeta(dataset_name, dataset_type, dataset_start_time, pickup_time_interval,
                                   time_window_interval, map_sections)

        dataset_creator = DatasetCreator(task_type, map_name, dataset_meta)

        if not tasks:
            dataset, tasks = dataset_creator.create(n_tasks=n_tasks, n_overlapping_sets=n_overlapping_sets)
        else:
            dataset, tasks = dataset_creator.create(n_tasks=n_tasks, n_overlapping_sets=n_overlapping_sets, tasks=tasks)

        dataset_file = 'datasets/' + dataset_name + '.yaml'

        with open(dataset_file, 'w') as outfile:
            yaml.safe_dump(dataset, outfile, default_flow_style=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('n_tasks', type=int, help='Number of tasks')

    parser.add_argument('n_overlapping_sets', type=int, help='Number of sets of consecutive tasks'
                        'A dataset with non-overlapping-tw contains only one set, '
                        'A dataset with overlapping-tw contains at least two sets')

    parser.add_argument('dataset_start_time', type=int, help='Dataset start time', default=1800)

    parser.add_argument('lower_bound', type=int, help='Lower bound for the pickup_time_interval and the '
                        'time_window_interval')

    parser.add_argument('upper_bound', type=int, help='Upper bound for the pickup_time_interval and the '
                        'time_window_interval')

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    create_datasets(args.n_tasks, args.n_overlapping_sets, args.dataset_start_time, args.lower_bound, args.upper_bound)
