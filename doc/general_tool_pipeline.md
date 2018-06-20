## General Tool Pipeline


### Manual Navigation

The first tool to get a broader grasp of the .dot files is the `graph_analyzer`. 
Here we implementet a vast amount of general and useful options to traverse the graph and get different kinds of information.

The next step is `bmwArchitecture to json`. This is a helper script to ease the creation of such a .json file as it will be used later on while creating further analysis files.
The resulting file should contains all Components from the to-be-architecture of BMW together with their Domain, Context Group and Abstraction Layer.
The .json file containing all information given to us already exists as `bmw-arch.json`.

The `json_validator` helps in checking whether the created .json file is in valid JSON-format.

Using the `grep_adapter` we did our namespace search, replacing all component names in `bmw-arch.json` with the search-terms which can be used later to create Component-nodes.
The resulting .json file containing all seach-terms we could find (within `task-depends.dot`) already exists as `task dependencies bmw-arch.json`.

### Doing pre-Analysis

Having done all the previous mentioned work, it is now possible to add one Node per Component, Domain, Context Group and Abstraction Layer 
into the .dot file (as already mentioned in our Analysis and Evaluation, we only worked on `task-depends.dot`).
This is done by calling the `parent_handler` from within the `src/` directory:

`./parent_handler task-depends.dot -j "task dependencies bmw-arch.json" -c`

The output graph is written to `out/parent_handler_output.gt`.

### Automatic Analysis

The `parent_handler` then is capable of doing two kinds of checks on the new graph:
Checking the Isolation Constraint and the Cohesion Constraint as defined in our Architecture Documentation.

To check the Isolation Constraint of all Components, Domains, Context Groups and Abstraction Layers, type

`./parent_handler ../out/parent_handler_output.gt -j "task dependencies bmw-arch.json" -v`

If any problems occur, those will be documented in a file located at `out/parent_handler_validation.txt` (note that no file will be created if everything is all right - all problems would also be reportedby the terminal)

Checking the Cohesion Constraint works as follows:

`./parent_handler ../out/parent_handler_output.gt -j "task dependencies bmw-arch.json" -p`

This will create several output files representing the connections between all Domains, Context Groups and Abstraction Layers each:
`domain.csv`, `context.csv` and `abstraction.csv` contain information about all colliding subnodes each.
`domain_component_collisions.csv`, `context_component_collisions.csv` and `abstraction_component_collisions.csv` contain information about all colliding Components each.

### Visualization





