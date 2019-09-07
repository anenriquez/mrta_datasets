# mrta_datasets

Get the requirements:
```
pip3 install -r requirements.txt
```

Add the task_allocation to your `PYTHONPATH` by running:

```
pip3 install --user -e .
```

## Create a dataset

Go to `dataset_lib/`

```
python3 create_dataset.py dataset_type n_tasks dataset_name --task_type task_type --poses_file poses_file --interval_type interval type --lower_bound lower_bound --upper_bound upper_bound 
```

Example: 
```
python3 create_dataset.py overlapping_tw 10 overlapping_1 --task_type generic_task

```

## Plot the dataset

Go to `datasets/plots`

```
python3 plot_datasety.py dataset_name dataset_type task_type interval_type file_extension

```

Example:

```
python3 plot_datasets.py overlapping_1 overlapping_tw generic_task random yaml
```
