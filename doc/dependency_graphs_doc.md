## Usage of `dependency_graphs`

For the creation of the graphs [graphviz](https://graphviz.readthedocs.io/en/stable/) is required

The main script is placed in the `/src`-directory of this project.
The help could be shown with `./dependency_graphs.py -h` or `./dependency_graphs.py --help`.

The following command assumes `parent_handler_output.gt`, `bmw-arch.json`, `task dependencies bmw-arch.json` are containd whithin the executing directory.

```
./dependency_graphs.py -g parent_handler_output.gt -jo bmw-arch.json -js "task dependencies bmw-arch.json"
```

would produce a bunch of graphs to the `../out/dependency_graphs/`-directory for manual analysis.

and a table to `stdout`:


```
Listing number of unconnected Graphs in Components, where number > 1 , i.e. a coherence violation.
Unconnected | Component name
------------+-------------------
# of uncon- | example_component_name
-nected     | 
components  | 
...

```

The intended usage is to look for Components with big amounts of unconnected components

One can also use the [task_depends](https://github.com/Waldleufer/archproj-bmwteam/blob/master/doc/task_depends_doc.md) 
tool to find the candidates to then inspect manually.

##

in the `../out/dependency_graphs/`-directory the following folders are created:

* **components**: 
  Visualizations of the isolation constraint of every component. 
    
##

* **abstraction_layers_inner**:
  Visualizations of the isolation constraint of every Abstraction Layer.
* **context_groups_inner**:
  Visualizations of the isolation constraint of every Context Group.
* **domains_inner**:
  Visualizations of the isolation constraint of every Domain. 
  
##

* **abstraction_layers_outer**:
  Analysis of the cohesion and coupling constraints between every two different Abstraction Layers
* **context_groups_outer**:
  Analysis of the cohesion and coupling constraints between every two different Context Groups
* **domains_outer**:
  Analysis of the cohesion and coupling constraints between every two different Domains
