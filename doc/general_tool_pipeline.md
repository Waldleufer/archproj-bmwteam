## General Tool Pipeline

This text shows how our tools can be used to create the analysis output we show in our `Analysis and Evaluation`. References to the `General Analysis Approach` inside this document are written like "(1)" and show that the described procedure corresponds to the specific step there.

### Manual Navigation

The first tool to get a broader grasp of the .dot files is the [`graph_analyzer`](graph_analyzer_doc.md).
Here we implemented a vast amount of general and useful options to traverse the graph and get different kinds of information (2).

The next step is [`bmwArchitecture_to_json`](bmwArchitecture_to_json_doc.md). This is a helper script to ease the creation of such a .json file as it will be used later on while creating further analysis files.
The resulting file should contains all Components from the to-be-architecture of BMW together with their Domain, Context Group and Abstraction Layer.
The `.json` file containing all information given to us already exists as `bmw-arch.json` (2).

The [`json_validator`](json_validator_doc.md) helps in checking whether the created `.json` file contains only valid Component search terms a.k.a. Component names (2).

Using the [`grep_adapter`](grep_adapter_doc.md) we did our namespace search, replacing all Component names in `bmw-arch.json` with the search-terms which can be used later to create Component-nodes.
The resulting `.json` file containing all search-terms we could find (within `task-depends.dot`) already exists as `task dependencies bmw-arch.json` which is assumed to be located within the `src/` directory for all following commands (3).

### Pre-Analysis

Having done all the previous mentioned work, it is now possible to add one Node per Component , Domain, Context Group and Abstraction Layer 
into the .dot file (as already mentioned in our `Analysis and Evaluation`, we only worked on `task-depends.dot`).
This is done by calling the [`parent_handler`](parent_handler_doc.md) from within the `src/` directory:

`./parent_handler.py task-depends.dot -j "task dependencies bmw-arch.json" -c`

The output graph is written to `../out/parent_handler_output.gt` (3,4).

### Semiautomatic Analysis

The [`parent_handler`](parent_handler_doc.md) then is capable of doing two kinds of checks on the new graph:
Checking the Isolation Constraint and the Cohesion Constraint as defined in our Architecture Documentation (5).

To check the Isolation Constraint of all Components, Domains, Context Groups and Abstraction Layers, type

`./parent_handler.py ../out/parent_handler_output.gt -j "task dependencies bmw-arch.json" -v`

If any problems occur, those will be documented in a file located at `../out/parent_handler_validation.txt` (note that no file will be created if everything is all right - all problems would also be reported by the terminal)

Checking the Cohesion Constraint works as follows (6):

`./parent_handler.py ../out/parent_handler_output.gt -j "task dependencies bmw-arch.json" -p`

This will create several output files representing the connections between all Domains, Context Groups and Abstraction Layers each (7):
`domain.csv`, `context.csv` and `abstraction.csv` contain information about all colliding subnodes each.
`domain_component_collisions.csv`, `context_component_collisions.csv` and `abstraction_component_collisions.csv` contain information about all colliding Components each.

#### Pre-Visualisation

The `.csv` files can be imported in our Google Spreadsheet "**Violations**" by selecting Cell D3 and navigating to file
-> import. Then simply upload the `.csv` file and under **Import Location** toggle the *"replace data at selected cell"* 
checkbox (8).

The sheet `Domain Vs` belongs to the file `domain.csv`.
The sheet `Weighted Domain Vs` belongs to `domain_component_collisions.csv`.
If the number of components changes due to manual analysis, these new numbers have to be updated in the Google Spreadsheet, too.
Same pattern works for *Context Groups* and *Abstraction Layer*.

The 3 matrices on the left hand side display information about the architecture's reality as follows:
Colored by line, one can see the maximum in the dark yellow/red highlighted cells and the lighter shades indicate a value is bigger than a percentage of 90% or 50% or 10% of the max value.
* `* shared nodes` (M1): the amount of nodes shared between two top layers when traversing the dependency graph.
* `* Weighted Violation by number of possible violations`(M2): `* shared nodes` weighted by `* - # of max violations`
* `* Weighted Violation by number of possible violations - TOP 4`(M3): same calculation as in M2, but now colored by line, one can see the maximum in the dark yellow/red highlighted cells and the lighter shades indicate the next smaller value.

The matices on the right hand side display information necessary for the weighting process:
* `* - # of max violations`: n * m, where n and m are the numbers of components of the different top layers.
* the small list below: number of components in each top layer.

### Visualization

There are two ways for visualizing the resulting data:
* Graphs could be rendered with the `--export*` option(s) of the [`graph_analyzer`](graph_analyzer_doc.md) script
* Matrices can use the `render_matrix_graphic.py` script located under `src/utils/`.

The last mentioned script works semi-automatic, which means there is no routine for parsing the data from an external file and the data has to be manually copied and pasted into the script itself. This step may be a bit tedious, but once it's done it enables a high degree of customization, which is often necessary for the visual appeal of the generated output file.

