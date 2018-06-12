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

The [graph-tool documentation](https://graph-tool.skewed.de/static/doc/index.html).

## Usage

* [graph_analyzer](doc/graph_analyzer_doc.md)
* [jsonparser](doc/jsonparser_doc.md)
* [json_validator](doc/json_validator_doc.md)
* [parent_handler](doc/parent_handler_doc.md)
* [grep_adapter](doc/grep_adapter_doc.md)
* [bmwArchitecture_to_json](/doc/bmwArchitecture_to_json_doc.md)
