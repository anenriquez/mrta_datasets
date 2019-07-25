import csv
import os
from src.task_factory import TaskLoader
from ropod.structs.task import Task as RopodTask
from src.task import Task as GenericTask
GenericTask.__name__ = 'GenericTask'
RopodTask.__name__ = 'RopodTask'


def get_datasets_dir():
    code_dir = os.path.abspath(os.path.dirname(__file__))
    main_dir = os.path.dirname(code_dir)

    datasets_dir = main_dir + '/datasets'

    return datasets_dir


def load_csv_dataset(dataset_name, task_cls, path):

    datasets_dir = get_datasets_dir()

    dataset_path = datasets_dir + path + dataset_name + '.csv'

    print(dataset_path)
    tasks = list()

    task_loader = TaskLoader(task_cls)

    try:
        with open(dataset_path, 'r') as file:
            csv_reader = csv.DictReader(file)
            for task_csv in csv_reader:

                task = task_loader.load_csv(task_csv)

                tasks.append(task)

    except IOError:
        print("File does not exist")

    return tasks


if __name__ == '__main__':

    path = '/overlapping_tw/generictask/random/'

    tasks = load_csv_dataset('overlapping_1', GenericTask, path)

    for task in tasks:
        print(task.id)
