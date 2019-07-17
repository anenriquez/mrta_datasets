import yaml
from ropod.structs.task import Task
from ropod.utils.datasets import to_csv


def read_dataset(dataset_path):
    with open(dataset_path, 'r') as file:
        dataset = yaml.safe_load(file)
    return dataset


def ropod_dataset_to_csv(ropod_dataset_path, cvs_path):
    """ Converts a list of ropod Task dictionaries to csv format
    and stores it in a *.csv file with the same name as the original dataset
    """
    dataset = read_dataset(dataset_path)
    tasks = dataset['tasks']
    list_task_dicts = list()

    for task_id, task in tasks.items():
        csv_dict = Task.to_csv(task)
        list_task_dicts.append(csv_dict)

    dataset_name = dataset_path.split('/')[-1].split('.')[0]
    csv_file = csv_path + dataset_name + '.csv'

    to_csv(list_task_dicts, csv_file)


if __name__ == '__main__':
    dataset_path = '../datasets/ropod/three_tasks.yaml'
    csv_path = '../datasets/thesis/'
    ropod_dataset_to_csv(dataset_path, csv_path)
