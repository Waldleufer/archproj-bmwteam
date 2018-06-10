## Usage of `jsonparser`

The script is placed in the `/src`-directory of this project.
The help could be shown with `./jsonparser.py -h` or `./jsonparser.py --help`.

The file `bmw-arch.json` was created by hand and contains all relevant information about the given to-be-architecture from BMW.
Its format is depicted in `bmwSoftwareArchitecture_archproj-bmwteam-schema.json`.

This scripts main use is to be a helper for other scripts or for manual use during verification.
It creates requested lists from above-mentioned .json file.
It can only use our specific .json format.

There are several possible ways of requesting information:

* `-d` or `--domain` prints all components belonging to one of the provided domain names

* `-c` or `--contextGroup` prints all components belonging to one of the provided context group names

* `-a` or `--abstractionLayer` prints all components belonging to one of the provided abstraction layer names

* `-all` prints every component occurring in the .json file

If any of those options don't find any results, nothing is printed. Several of the internal functions are used in other scripts.
