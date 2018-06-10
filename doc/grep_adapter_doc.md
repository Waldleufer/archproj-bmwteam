## Usage of `grep_adapter`

The help tool is placed in the `/src`-directory of this project.
The help could be shown with `./grep_adapter.py -h` or `./grep_adapter.py --help`.

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

The tool implements a case insensitive search for terms in the dot File what was useful to validate the terms of the
HLA diagram. To search for nodes we would reccomend to use the graph_analyzer.py tool.

For example, if we search for the term "apple" in the given graph with `./grep_adapter.py ../tests/test01.dot "apple"` 
(assuming `/src` is the current working directory) the following output is shown:

```
Fruits -> Apple
Apple -> Green Apple
Apple -> Red Apple
```
As we see, all lines containing `Apple` are shown.

To get the intersection of two terms we could type `term1&term2` e.g.
`./grep_adapter.py ../tests/test01.dot "apple&green"` this would produce:

```
Apple -> Green Apple
```
This means from all lines which contain the term "Apple" only one line which is shown above does also contain the term "Green".

A  search for multiple terms can also be done by `term1;term2` e.g.
`./grep_adapter.py ../tests/test01.dot "apple;banana"`

The output for this example would be:
```
Fruits -> Apple
Apple -> Green Apple
Apple -> Red Apple
Fruits -> Banana
```

A combined search for multiple intersections of terms can also be done by `term1&term2;term3&term4` e.g.

```bash
./grep_adapter.py ../tests/test01.dot "apple&green;banana"
```

What results in 
```
Apple -> Green Apple
Fruits -> Banana
```
as expected.
