# redis-cluster-demo

This is a demo for **Redis** in **cluster** mode using **Docker**. Created to be used in CS5204 Project Presentation.

## Options

|command         |description                          |default                      |
|----------------|-------------------------------------|-----------------------------|
|`-c/--create`   |creates a cluster                    |false                        |
|`-s/--stop`     |stops the cluster (deletes all data) |false                        |
|`-n`            |used with `--create`, specifies number of nodes in the cluster |4  |

## Example

To start a cluster, run
```
python spawner.py --create -n 16
```

To kill a cluster that is already running, run
```
python spawner.py --stop
```

> **Note:** The **Stop** relies on temporary files created at redis-confs folder
