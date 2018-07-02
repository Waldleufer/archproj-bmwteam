## Usage of `task_depends`

The tool is placed in the `/src`-directory of this project.
A short help message can be obtained by entering `./task_depends.py -h` or `./task_depends.py --help`.

The script computes the size (number of nodes) of the dependency graph for each node in a graph. 
With this, one can get a list of nodes that need the most components.

The more interesting feature of this tool is the ability to reverse `-r` the direction of all dependencies 
and proceed with the same analysis method as mentioned before.
This generates a list of nodes that are most required by other nodes.

Assuming packages have to be rebuild when a dependency changes, then these are the packages with 
the biggest impact on other packages.

### Examples:

The following use-cases refer to the `test01.dot`-file which could be found in the `/tests`-folder.
This file represents a graph with the following hierarchy:

```
[Fruits]
  ├─[Banana]
  ├─[Pear]
  ├─[Mango]
  └─[Apple]
       ├─[Red Apple]
       └─[Green Apple]
           ├─[Light Green]
           └─[Dark Green]
```

Using the tool with 
```bash
./task_depends.py ../tests/test01.dot 
```
produces the following output.
```
Count | Task Name
------+-------------------
    6 | Fruits
    2 | Apple
    2 | Green
    0 | Banana
    0 | Dark Green
    0 | Green Apple
    0 | Light Green
    0 | Mngo
    0 | Pear
    0 | Red Apple
```

Using the tool with the inverted option:
````
./task_depends.py ../tests/test01.dot -r
````
One gets:
```
Count | Task Name
------+-------------------
    2 | Green Apple
    2 | Red Apple
    1 | Apple
    1 | Banana
    1 | Dark Green
    1 | Light Green
    1 | Mango
    1 | Pear
    0 | Fruits
    0 | Green
```
Where _Count_ does display the number of inverted dependencies a.k.a. how required a node is by other nodes.