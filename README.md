# archproj-bmwteam

## Installation

Install all required native libraries for your Operating System as described in the 
[graph-tool installation instructions](https://git.skewed.de/count0/graph-tool/wikis/installation-instructions#native-installation).

Please ensure that all packages are installed and available for `python3`.

**Note for Linux Users:** It might be necessary to import a `gpg`-key as superuser to be able to add
the installation repository to the system. The key import could be done with the following command:
```
sudo apt-key adv --keyserver pgp.skewed.de --recv-key 612DEFB798507F25
```

It may also be possible that the some warnings about `matplotlib` occur. This could be resolved by
installing one additional package on the system. On Ubuntu-like distributions this could be achieved
with:
```bash
sudo apt install python3-matplotlib
```

## Documentation

The [graph-tool documentation](https://graph-tool.skewed.de/static/doc/index.html)

## Usage

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
As we see, the node with the index `3` is the root-node of this graph. But since graphs with cyclic
dependencies are possible, graphs with no root-node by definition could also show up.

To detect cycles, we can use the `--cycle` option to detect them. With our example, the following
output is shown:
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
./graph_analyzer.py ../tests/test01.dot -r -s `cat search_terms.txt`
```
and we get the exact same result as shown before. By this way, it is easy to create and handle
huge lists of search terms or node-vertices without typing them manually in the terminal window.

Note that the second part is enclosed in back-ticks <code>\`</code> so that the `bash` interprets
the resulting sequence (in this case `1 6 0`) as arguments for the first command part.

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
The `--raw` output works also in combination with `--children`, `--top`, `--subgraphs` and
`--shared` option.

