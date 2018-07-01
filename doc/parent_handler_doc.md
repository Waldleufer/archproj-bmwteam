## Usage of `parent_handler`

The script is placed in the `/src`-directory of this project.
The help could be shown with `./parent_handler.py -h` or `./parent_handler.py --help`.

This script makes use of `graph_analyzer.py` and `jsonparser.py` and must be called from withing the `/src` folder.
It gets a path to a graph file (either .dot or .gt) and to a .json file (in the same format as `jsonparser.py` uses it).
Using those it can create new parents in the graph and save it to `/out` or validate some things in it.

The required argument is:

* `GRAPH_FILE` what should be:

    either a `.dot` file when using the `-c` option as specified below,

    or the `.gt` file **that results** from the `-c` operation for all other options.

The optional arguments are:

* `-j JSON_FILE` or `--json_file JSON_FILE` is the argument where to specify the `JSON_FILE` that shall be used.

* `-c` or `--createParents` takes all components from the .json file (usually `task dependencies bmw-arch.json`) and finds every occurrence of the names in the graph - details to the .json and search follow later. Components containing "kein Match" or "no Match" are skipped. For each component a new node with the exact same name is created within the graph. This node points towards any node that could be found using its name. Afterwards every domain, context group and abstraction layer is extracted from the .json file and more nodes are created (again eac one for every name) - those nodes then point towards their respective component nodes.

* `-v` or `--validate` takes all components from the .json file (usually `task dependencies bmw-arch.json`) and finds every occurrence of the names in the graph just like when using `-c`. 
For every component, Domain, Context Group and Abstraction Layer all childrens subgraphs are inspected. 
If they intersect with each other directly or even indirectly over other subgraphs from other children, then everything is considered fine. 
If there are at least 2 nodes not connected directly or indirectly via subgraphs, the whole component and its childrens connections are printed and also stored as `parent_handler_validation.txt` in the `/out` directory.

* `-p` or `--print_top_level_connections` takes the given `.gt` file and analyzes the top level connections.
Output files are placed in the out directory (`../out/`) and are named `domain.csv`, `context.csv` and `abstraction.csv`, as well as `domain_component_collisions.csv`, `context_component_collisions.csv` and `abstraction_component_collisions.csv` representing the connections either between all domains, all contextGroups or all abstractionLayers. The first three count all overlapping nodes in total, the last three ones count overlapping components.
In the `.csv` files a matrix containing the overlapping information is shown. 
The top row shows the TopLevel Term sequence of the columns and if transposed it shows the sequence of the rows.



The file `task dependencies bmw-arch.json` is a variant of `bmw-arch.json` where all components names were altered in a way we believe to best reflect search terms needed to find the corresponding nodes in the provided .dot files using `graph_analyzer.py`. These names are built like "App;CD&Speech". Inside the search terms ";" is used as union, while "&" stands for intersection. Also "&" binds stronger than ";".


An example is given in `test03.dot` and `test03.json`:

First let's take a look at the whole `test03.dot`

```
vtx[0] in: 0 out: 2 val: v00
├─ vtx[5] in: 1 out: 0 val: v05
└─ vtx[6] in: 2 out: 0 val: v06
vtx[1] in: 0 out: 2 val: v01
├─ vtx[6] in: 2 out: 0 val: v06
└─ vtx[7] in: 2 out: 0 val: v07
vtx[2] in: 0 out: 1 val: v02
└─ vtx[7] in: 2 out: 0 val: v07
vtx[3] in: 0 out: 2 val: v03
├─ vtx[8] in: 1 out: 0 val: v08
└─ vtx[9] in: 2 out: 0 val: v09
```

whereas `test03.json` contains

```
{
  "just": [
    {
      "a": [
        {
          "test": [
            {
              "v00;v01;v02;v03": {
                "domain": "Information about any Context Groups & Co. is not given for privacy purposes.",
                "contextGroup": "Information about any Context Groups & Co. is not given for privacy purposes.",
                "abstractionLayer": "Information about any Context Groups & Co. is not given for privacy purposes."
              }
            }
          ]
        }
      ]
    }
  ]
}
```

Typing `./parent_handler ./test03.dot -j ./test03.json -c` creates a parent node called "v00;v01;v02;v03" as contained in the .json file. According to how the search works with this name, `parent_handler.py` finds the nodes `v00`, `v01`, `v02` and `v03`, which are then connected to the parent node resulting in the following output graph called `parent_handler_output.gt`:

```
vtx[12] in: 0 out: 4 val: v00;v01;v02;v03
├─ vtx[0] in: 1 out: 2 val: v00
│  ├─ vtx[5] in: 1 out: 0 val: v05
│  └─ vtx[6] in: 2 out: 0 val: v06
├─ vtx[1] in: 1 out: 2 val: v01
│  ├─ vtx[6] in: 2 out: 0 val: v06
│  └─ vtx[7] in: 2 out: 0 val: v07
├─ vtx[2] in: 1 out: 1 val: v02
│  └─ vtx[7] in: 2 out: 0 val: v07
└─ vtx[3] in: 1 out: 2 val: v03
   ├─ vtx[8] in: 1 out: 0 val: v08
   └─ vtx[9] in: 2 out: 0 val: v09
```

Using this new graph (when only checking components, the old graph would work as well) like `./parent_handler ./parent_handler_output.gt -j ./test03.json --validate_components_only` starts a validation (only of all components) as described. This example won't show details about Domains, Context Groups or Abstraction Layers - thats why this option was implemented. Since `v00`, `v01` and `v02` are connected directly or indirectly via subgraphs but `v03` is in no way connected, the validation will print a warning containing all children of the node `v00;v01;v02;v03` and their connections:
It puts

```
the following nodes and their subgraphs aren't connected even though they share the same parent:
v00;v01;v02;v03:
['0', '1', '2']
['3']
```

into the terminal and writes

```
v00;v01;v02;v03
0,1,2
3

```

to the file `parent_handler_validation.txt`. Internally this is saved as follows:

```
[[[0, 1, 2], [3], "v00;v01;v02;v03"]]
or
[[[node1, node2], [node3, node4], "parent1_name"], [[node5], [node6, node7, node8], "parent2_name"]]
```
