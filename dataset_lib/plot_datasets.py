from dataset_lib.load_dataset import load_yaml_dataset
import dateutil.parser
from datetime import datetime, timedelta

from dataset_lib.plot_dataset import plot_dataset_plotly

if __name__ == '__main__':

    # Uses the same initial time for all datasets
    initial_time_str = "2020-01-23T08:00:00.000000"
    initial_time = dateutil.parser.parse(initial_time_str).timestamp()

    experiments = {'exp_1': ['overlapping_tight_25_5_1', 'overlapping_loose_25_5_1', 'overlapping_random_25_5_1'],
                   'exp_3': ['overlapping_random_5_5_1', 'overlapping_random_10_5_1', 'overlapping_random_15_5_1',
                             'overlapping_random_20_5_1', 'overlapping_random_25_5_1', 'overlapping_random_30_5_1',
                             'overlapping_random_35_5_1', 'overlapping_random_40_5_1', 'overlapping_random_45_5_1',
                             'overlapping_random_50_5_1'],
                   'exp_4': ['nonoverlapping_random_50_1'],
                   'exp_5': ['overlapping_random_50_10_1']}

    for experiment_name, datasets in experiments.items():
        print("Experiment: ", experiment_name)
        earliest_time = float('inf')
        latest_time = - float('inf')

        for dataset_name in datasets:
            print("Dataset: ", dataset_name)
            dataset = load_yaml_dataset(dataset_name, 'task')

            for task in dataset.get('tasks'):
                pickup_time = task.earliest_pickup_time + initial_time
                delivery_time = task.latest_pickup_time + initial_time + task.plan.estimated_duration
                if pickup_time < earliest_time:
                    earliest_time = pickup_time

                if delivery_time > latest_time:
                    latest_time = delivery_time

        xmin = datetime.fromtimestamp(earliest_time) - timedelta(seconds=60)
        xmax = datetime.fromtimestamp(latest_time) + timedelta(seconds=60)

        print("xmin: ", xmin)
        print("xmax: ", xmax)

        # Plot datasets from an experiment with the same xmin and xmax

        for dataset_name in datasets:
            dataset = load_yaml_dataset(dataset_name, 'task')
            plot_dataset_plotly(dataset_name, dataset['tasks'], initial_time_str, show=True, xmin=xmin, xmax=xmax,
                                file_name=experiment_name + '_' + dataset_name)

