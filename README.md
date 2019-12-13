# redis-cluster-demo

This is a demo for **Redis** in **cluster** mode using **Docker**. Created to be used in CS5204 Project Presentation.

## Options

|command         |description                          |default                      |
|----------------|-------------------------------------|-----------------------------|
|`-c/--create`   |creates a cluster                    |False                        |
|`-e/--extend`   |adds a node to the cluster           |False                        |
|`-s/--stop`     |stops the cluster (deletes all data) |False                        |
|`-n`            |used with `--create`, specifies number of nodes in the cluster |4  |
|`-p`            |starting port number                 |7000                         |
|`--host`        |used with `--extend`, specifies address of a node|None             |
|`--host-port`   |used with `--extend`, specifies port of host node|7000             |

## Example

To start a cluster, run
```
python spawner.py --create -n 4
```

To kill a cluster that is already running, run
```
python spawner.py --stop
```

To extend a cluster by one node, run
```
python spawner.py --extend --host [ip address of a node in the cluster] --host-port [port of that node]
```

> **Note:** The **Stop** command relies on temporary files created at redis-confs folder
