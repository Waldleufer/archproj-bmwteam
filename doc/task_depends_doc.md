## Usage of `task_depends`

The tool is placed in the `/src`-directory of this project.
A short help message can be obtained by entering `./task_depends.py -h` or `./task_depends.py --help`.

The script computes the size (number of nodes) of the dependency graph for each node in a graph. With this, one can get a list of nodes that need the most components.

The more interresting feature of this tool is the ability to reverse `-r` the direction of all dependencies and the doing the same analysis as above.
This generates a list of nodes that are most required by other nodes.

If it is assumed that packages have to be rebuild, when a dependency changes, then these are the packages that have the biggest impact on other packages when changed.
