import csv
from datasets.task import Task
import os
from datasets.utils.config_logger import config_logger
import logging


def load_dataset(dataset_name):

    code_dir = os.path.abspath(os.path.dirname(__file__))
    main_dir = os.path.dirname(code_dir)

    config_logger(main_dir + '/config/logging.yaml')
    logger = logging.getLogger('dataset')

    dataset_path = code_dir + '/thesis/' + dataset_name

    tasks = list()

    try:
        with open(dataset_path, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:

                id = row['id']
                earliest_start_time = float(row['earliest_start_time'])
                latest_start_time = float(row['latest_start_time'])
                pickup_pose_name = row['pickup_pose_name']
                delivery_pose_name = row['delivery_pose_name']

                task = Task(id, earliest_start_time, latest_start_time, pickup_pose_name, delivery_pose_name)

                tasks.append(task)

    except IOError:
        print("File does not exist")
        logger.exception("File does not exist")

    return tasks
