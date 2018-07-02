## Usage of `dependency_graphs`

For the creation of the graphs [graphviz](https://graphviz.readthedocs.io/en/stable/) is required

The main script is placed in the `/src`-directory of this project.
The help could be shown with `./dependency_graphs.py -h` or `./dependency_graphs.py --help`.

The following comand assumes `parent_handler_output.gt`, `bmw-arch.json`, `task dependencies bmw-arch.json` are containd whithin the executing directory.

```
./dependency_graphs.py -g parent_handler_output.gt -jo bmw-arch.json -js "task dependencies bmw-arch.json"
```

would produce a bunch of graphs to the `../out/dependency_graphs/`-directory for manual analysis.

and a table to `stdout`
```
Listing number of unconnected Graphs in Components, where number > 1, i.e. a coherence violation.
Unconnected | Component name
------------+-------------------
# of uncon- | example_component_name
-nected     | 
components  | 
...

```
