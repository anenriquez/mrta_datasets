# mrta_datasets

Get the requirements:
```
pip3 install -r requirements.txt
```

Add the task_allocation to your `PYTHONPATH` by running:

```
sudo pip3 install -e .
```

## Create a dataset

Go to `src/` 

```
python3 create_dataset.py dataset_type n_tasks dataset_name --task_type task_type --poses_file poses_file --interval_type interval type --lower_bound lower_bound --upper_bound upper_bound 
```

Example: 
```
python3 create_dataset.py overlapping_tw 10 overlapping_1 --task_type RopodTask

```

## Plot the dataset

Go to `datasets/plots`

```
python3 plot_datasety.py dataset_type task_type interval_type file_extension

```

Example:

```
python3 plot_datasets.py non_overlapping_tw ropod_task random yaml
```
