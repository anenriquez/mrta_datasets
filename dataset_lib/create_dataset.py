import argparse
import logging
import os

import yaml

from dataset_lib.config.creators import DatasetCreator

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
                        default=10)

    parser.add_argument('--time_window_upper_bound', type=int, help='Time window interval upper bound (seconds)'
                        'The time window interval is the time between tasks, i.e., the time between'
                        'the latest finish time of a task and the earliest start time of the next',
                        default=300)

    parser.add_argument('--dataset_start_time', type=int, help='Earliest pickup time of the first task in each set '
                        'of tasks', default=900)

    parser.add_argument('--task_type', type=str, help='task type', choices=['task'], default='task')

    parser.add_argument('--map_name', type=str, help='Name of the map to get poses from', default='brsu')

    parser.add_argument('--map_sections', type=list, help='Name of sections in the map to take goal poses from',
                        default=['square', 'street', 'faraway'])

    args = parser.parse_args()

    dataset_path = 'datasets/'

    dataset_creator = DatasetCreator(args.map_name)

    dataset_type = 'overlapping' if args.n_overlapping_sets > 1 else 'non_overlapping'

    dataset_name = dataset_type + '_' + args.interval_type
    dataset_id = 0

    for file_ in os.listdir(dataset_path):
        if os.path.isfile(dataset_path + file_) and file_.startswith(dataset_name):
            dataset_id = int(file_.split('_')[-1].split('.')[0])
    dataset_id += 1

    dataset_name = dataset_name + '_' + str(dataset_id)

    print("Dataset name: ", dataset_name)

    logging.basicConfig(level=logging.DEBUG)

    dataset = dataset_creator.create(args.task_type,
                                     dataset_type,
                                     args.n_tasks,
                                     args.n_overlapping_sets,
                                     dataset_name,
                                     interval_type=args.interval_type,
                                     pickup_time_lower_bound=args.pickup_time_lower_bound,
                                     pickup_time_upper_bound=args.pickup_time_upper_bound,
                                     time_window_lower_bound=args.time_window_lower_bound,
                                     time_window_upper_bound=args.time_window_upper_bound,
                                     dataset_start_time=args.dataset_start_time,
                                     map_sections=args.map_sections)

    dataset_file = dataset_path + dataset_name + '.yaml'

    with open(dataset_file, 'w') as outfile:
        yaml.safe_dump(dataset, outfile, default_flow_style=False)

