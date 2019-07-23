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
python3 create_dataset.py --help
```

Example: 
```
python3 create_dataset.py overlapping_tw 10 overlapping_1 --task_cls_name RopodTask

```

