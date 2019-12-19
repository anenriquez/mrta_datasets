# mrta_datasets

Installation

```
pip3 install -r requirements.txt
```

```
pip3 install --user -e .
```

## Create a dataset

Go to `dataset_lib/`

```
python3 create_dataset.py dataset_type n_tasks dataset_name 
```

Example: 
```
python3 create_dataset.py overlapping_tw 10 overlapping_1

```

## Plot the dataset

Go to `dataset_lib/`

```
python3 plot_datasety.py dataset_name dataset_type task_type interval_type

```

Example:

```
python3 plot_datasets.py overlapping_1 overlapping_tw generic_task random
```
