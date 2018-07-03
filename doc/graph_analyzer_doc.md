## Usage of `graph_analyzer`

The main script is placed in the `/src`-directory of this project.
The help could be shown with `./graph_analyzer.py -h` or `./graph_analyzer.py --help`.

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

Internally, each node (a.k.a. vertex) gets its own unique ID after loading. Since the internals of
`graph-tool` creates a binary-spanning-tree, the node IDs may not align with an increasing order.
For example, if we print the given graph with `./graph_analyzer.py ../tests/test01.dot -c 3` 
(assuming `/src` is the current working directory) the following output is shown:

```
vtx[3] in: 0 out: 4 val: Fruits
├─ vtx[0] in: 1 out: 2 val: Apple
│  ├─ vtx[4] in: 1 out: 2 val: Green
│  │  ├─ vtx[5] in: 1 out: 0 val: Light
│  │  └─ vtx[2] in: 1 out: 0 val: Dark
│  └─ vtx[8] in: 1 out: 0 val: Red
├─ vtx[1] in: 1 out: 0 val: Banana
├─ vtx[7] in: 1 out: 0 val: Pear
└─ vtx[6] in: 1 out: 0 val: Mango
```

As we see, the node with the index `3` is the root-node of this graph. Since the indices may change
when the graph file gets extended, we can also use the name of the node like
`./graph_analyzer.py ../tests/test01.dot -c Fruits` to get the exact same result as shown before and
don't have to fear that the behavior of the command will change when the *.dot file gets edited.

In this case, we knew from the start that `Fruits` was the root-node. However this is not always
clear and since graphs with cyclic dependencies are also possible, graphs with no root-node by
definition could show up as well.

But if we want to detect potential root-nodes, we could use the `--subgraphs` option, which analyzes
the relations of all nodes to each other and print a list of sub-graphs occurring in the main graph.

```
Found 3 sub-graphs:
sub[0] has 4 children, val: Apple
         - includes sub[4]  val: Green
sub[3] has 8 children, val: Fruits
         - includes sub[0]  val: Apple
         - includes sub[4]  val: Green
sub[4] has 2 children, val: Green
```

If we look now for the node which contains the most children and sub-graphs, we will recognize that
the node `Fruits` is most likely our searched root-node.

If we want to find cycles in the graph, we can use the `--cycle` option to detect them. With our
example, the following output is shown:
```
Graph is a DAG. No cycles found!
```
This means our example is a directed acyclic graph (DAG) and has no cyclic dependencies. However,
if there occurs a cycle in the graph, the involved indices and values are getting listed
accordingly.

A case sensitive search for one ore multiple terms can be done with `-s` or `--search` e.g.
`./graph_analyzer.py ../tests/test01.dot -s an Ap`

The output for this example would be:
```
Found 2 results for 'an':
vertex[1] Banana
vertex[6] Mango
Found 1 results for 'Ap':
vertex[0] Apple
```
To reduce the work of defining the search terms over and over again, we can also store them in a
regular text file and pipe the content via `cat` into the script. Given the file `search_terms.txt`
with the following content:
```
an Ap
``` 
Now we can simply invoke
```bash
./graph_analyzer.py ../tests/test01.dot -s `cat search_terms.txt`
```
and we get the exact same result as shown before. By this way, it is easy to create and handle
huge lists of search terms or node-vertices without typing them manually in the terminal window.

Note that the second part is enclosed in back-ticks <code>\`</code> so that the `bash` interprets
the resulting sequence (in this case `an Ap`) as arguments for the first command part.

We also can use the search-option in combination with the `--raw` or `-r`-option to provide a 
machine readable output of the search results. This means only the indices are printed to std-out
which could be piped into a file or to another program. Let's try this by searching for the
character sequence "an" and "Ap" like before and print out the details about the found nodes with
the `--print` or `-p`-option:
```bash
./graph_analyzer.py ../tests/test01.dot -p `./graph_analyzer.py ../tests/test01.dot -r -s an Ap`
```

The resulting output is:
```
vtx[1] in: 1 out: 0 val: Banana
vtx[6] in: 1 out: 0 val: Mango
vtx[0] in: 1 out: 2 val: Apple
```
The `--raw` output works also in combination with `--children`, `--subgraphs` and `--shared` 
option.

It is also possible to create groups where various nodes get merged together into one master-node.
Therefore the `--group` option requires the name of the new master-node and than a list of all
nodes who should be merged together. On this behalf, it is not necessary to provide all entries as
indices (which is also possible). Usually, it is sufficient enough to use the names of the nodes
as long as they match the exact spelling as provided in the source file. Even both notations could
be mixed up and used at the same time like stated in the following example. 
```bash
./graph_analyzer.py ../tests/test01.dot --group ApplesWithDifferentColors 5 Green 8 Dark
```

The output would be:
```
vtx[3] in: 0 out: 4 val: Fruits
├─ vtx[0] in: 1 out: 1 val: Apple
│  └─ vtx[9] in: 1 out: 0 val: ApplesWithDifferentColors
├─ vtx[1] in: 1 out: 0 val: Banana
├─ vtx[7] in: 1 out: 0 val: Pear
└─ vtx[6] in: 1 out: 0 val: Mango
```

Note that the indices `5` and  `8` got included in the new `ApplesWithDifferentColors`-node as well
as the nodes with the indices `2` and `8`, which got selected by their name. However, the rest of
the nodes and their indices remain the same. If a interpretation of a number as name is necessary,
we can escape the input with a dot, followed by the number we want to use as node name (e.g. `.5`).

