import argparse
from dataset_lib.load_dataset import load_yaml_dataset
import yaml


def postpone_tasks(tasks, time_):
    tasks_dict = dict()
    for task in tasks:
        task.earliest_pickup_time += time_
        task.latest_pickup_time += time_
        tasks_dict[task.task_id] = task.to_dict()

    return tasks_dict


if __name__ == '__main__':

    "Postpones a dataset by the given time (in seconds)"

    parser = argparse.ArgumentParser()

    parser.add_argument('dataset_name', type=str, help='Name of the dataset')
    parser.add_argument('time', type=int, help='Time to displace in seconds')

    parser.add_argument('--task_type', type=str, help='Task type', choices=['task'], default='task')

    args = parser.parse_args()

    dataset = load_yaml_dataset(args.dataset_name, args.task_type)

    tasks = postpone_tasks(dataset['tasks'], args.time)

    dataset['tasks'] = tasks

    dataset_file = 'datasets/' + args.dataset_name + '_1.yaml'
    print(dataset_file)

    with open(dataset_file, 'w') as outfile:
        yaml.safe_dump(dataset, outfile, default_flow_style=False)


