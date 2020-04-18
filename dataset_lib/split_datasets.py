import argparse
from dataset_lib.load_dataset import load_yaml_dataset
import yaml


def get_task_scalability_dataset(n_tasks_set, tasks):
    tasks_per_set = dict()
    new_tasks = dict()
    for task in tasks:
        if task.set_number not in tasks_per_set:
            tasks_per_set[task.set_number] = list()
        tasks_per_set[task.set_number].append(task)

    for set_number, tasks in tasks_per_set.items():
        tasks_in_set = sorted(tasks, key=lambda task: task.earliest_pickup_time)[:n_tasks_set]

        for t in tasks_in_set:
            new_tasks[t.task_id] = t.to_dict()

    return new_tasks


if __name__ == '__main__':

    "Split a dataset of n tasks into sets of n_tasks"

    parser = argparse.ArgumentParser()

    parser.add_argument('dataset_name', type=str, help='Name of the dataset')
    parser.add_argument('new_dataset_name', type=str, help='Name of the new dataset')
    parser.add_argument('n_tasks_set', type=int, help='Number of tasks per set')

    parser.add_argument('--task_type', type=str, help='Task type', choices=['task'], default='task')

    args = parser.parse_args()

    dataset = load_yaml_dataset(args.dataset_name, args.task_type)

    tasks = get_task_scalability_dataset(args.n_tasks_set, dataset['tasks'])

    dataset['tasks'] = tasks

    dataset_file = 'datasets/' + args.new_dataset_name + '.yaml'
    print(dataset_file)

    with open(dataset_file, 'w') as outfile:
        yaml.safe_dump(dataset, outfile, default_flow_style=False)