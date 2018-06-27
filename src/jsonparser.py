#!/usr/bin/env python3

# Copyright 2018 archproj-bmwteam
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import json
import argparse

JSON_FILE_PATH = "../tests/bmw-arch.json"


def _breakdown_dict(dic: dict):
    """
    Breaks down our whole bmw-json schema into a single dictionary.
    :param dic: a dictionary in our bmw-json schema.
    :return: a single dictionary containing every module and its "domain", "contextGroup" and "abstractionLayer" without
    any deeper lists or dictionaries.
    """
    modules = {}
    for k1, v1 in dic.items():  # dict 1 - k1=contextGroups, v1=List of context group
        for l1 in v1:  # list 1 - l1=dict of hw-levels
            for k2, v2 in l1.items():  # dict 2-k2=e.g.connectivity, v2=e.g.list of dict with presentation, services, ..
                for l2 in v2:  # list 2
                    for k3, v3 in l2.items():  # dict 3
                        for l3 in v3:  # list 3
                            for k4, v4 in l3.items():  # dict 4
                                modules[k4] = v4
    return modules


def all_components(file_path: str):
    """
    Returns a list of every component inside a json file using our bmw-json schema
    :param file_path: path to the file
    :return: a list of every component in the given json file.
    """

    path = file_path
    if path == "":
        path = JSON_FILE_PATH
    data_file = open(path, encoding="utf-8")
    dic = json.loads(data_file.read())

    modules = _breakdown_dict(dic)
    componentlist = []
    for k, v in modules.items():
        componentlist.append(k)

    return componentlist


def search_by_domain(file_path: str, domain: str):
    """
    Searches a dictionary in our bmw-json schema for every module inside the given domain.
    param file_path: the path to the json file to be searched. It should be in our bmw-json schema.
    :param file_path: path to the file
    :param domain: the domain of which content is requested.
    :return: a list of every module inside the given domain.
    """
    # This can be used to check whether everything was inputted correctly into our json file.
    # domains = get_domainlist()
    path = file_path
    if path == "":
        path = JSON_FILE_PATH
    data_file = open(path, encoding="utf-8")
    dic = json.loads(data_file.read())

    modules = _breakdown_dict(dic)
    domainlist = []
    for k, v in modules.items():
        # if(v["domain"] not in domains and v["domain"] is not None):
        if v["domain"] == domain:
            domainlist.append(k)
    return domainlist


def search_by_context(file_path: str, context: str):
    """
    Searches a dictionary in our bmw-json schema for every module inside the given contextGroup.
    :param file_path: the path to the json file to be searched. It should be in our bmw-json schema.
    :param context: the contextGroup of which content is requested.
    :return: a list of every module inside the given contextGroup.
    """
    # This can be used to check whether everything was inputted correctly into our json file.
    # contexts = get_context_groups()

    path = file_path
    if path == "":
        path = JSON_FILE_PATH
    data_file = open(path, encoding="utf-8")
    dic = json.loads(data_file.read())

    modules = _breakdown_dict(dic)
    contextlist = []
    for k, v in modules.items():
        # if(v["contextGroup"] not in contexts and v["contextGroup"] is not None):
        if v["contextGroup"] == context:
            contextlist.append(k)
    return contextlist


def search_by_abstraction(file_path: str, abstraction_layer: str):
    """
    Searches a dictionary in our bmw-json schema for every module inside the given contextGroup.
    :param file_path: the path to the json file to be searched. It should be in our bmw-json schema.
    :param abstraction_layer: the abstractionLayer of which content is requested.
    :return: a list of every module inside the given abstractionLayer.
    """
    # This can be used to check whether everything was inputted correctly into our json file.
    # abstraction_layers = get_abstraction_layers()
    path = file_path
    if path == "":
        path = JSON_FILE_PATH
    data_file = open(path, encoding="utf-8")
    dic = json.loads(data_file.read())

    modules = _breakdown_dict(dic)
    abstraction_layer_list = []
    for k, v in modules.items():
        # if(v["abstractionLayer"] not in abstraction_layers and v["abstractionLayer"] is not None):
        if v["abstractionLayer"] == abstraction_layer:
            abstraction_layer_list.append(k)
    return abstraction_layer_list


def get_domains(file_path: str):
    path = file_path
    if path == "":
        path = JSON_FILE_PATH
    data_file = open(path, encoding="utf-8")
    dic = json.loads(data_file.read())

    modules = _breakdown_dict(dic)
    domains = []
    for k,v in modules.items():
        dom = v["domain"]
        if (dom not in domains) and (dom is not None):
            domains.append(dom)

    domains.sort()
    return domains


def get_context_groups(file_path: str):
    path = file_path
    if path == "":
        path = JSON_FILE_PATH
    data_file = open(path, encoding="utf-8")
    dic = json.loads(data_file.read())

    modules = _breakdown_dict(dic)
    context_groups = []
    for k, v in modules.items():
        con_group = v["contextGroup"]
        if (con_group not in context_groups) and (con_group is not None):
            context_groups.append(con_group)

    context_groups.sort()
    return context_groups


def get_abstraction_layers(file_path: str):
    path = file_path
    if path == "":
        path = JSON_FILE_PATH
    data_file = open(path, encoding="utf-8")
    dic = json.loads(data_file.read())

    modules = _breakdown_dict(dic)
    abstraction_layers = []
    for k, v in modules.items():
        abstract_layer = v["abstractionLayer"]
        if (abstract_layer not in abstraction_layers) and (abstract_layer is not None):
            abstraction_layers.append(abstract_layer)

    abstraction_layers.sort()
    return abstraction_layers


def line_print(component_list: list):
    for component in component_list:
        print(component)


def main(argv):
    """
    Main function which parses the passed arguments.

    :param argv: the argument list passed by the command line
    """
    parser = argparse.ArgumentParser(description="A adapter to search for a component from the json file")
    parser.add_argument('file', type=str, metavar='FILE', help="file that shall be searched.")
    parser.add_argument('-d', '--domain', type=str, nargs='+', metavar='DOMAIN_NAME',
                        help="find all names of a given domain")
    parser.add_argument('-c', '--contextGroup', type=str, nargs='+', metavar='CONTEXT_GROUP_NAME',
                        help="find all names of a given context group")
    parser.add_argument('-a', '--abstractionLayer', type=str, nargs='+', metavar='ABSTRACTION_LAYER_NAME',
                        help="find all names of a given abstraction layer")
    parser.add_argument('-all', action='store_true', help="output of all components regardless of position")
    args = parser.parse_args()

    if not args.file:
        print("Try 'jsonparser -h' for more information.")
        sys.exit(1)

    if args.domain:
        for domain in args.domain:
            line_print(search_by_domain(args.file, domain))

    if args.contextGroup:
        for context in args.contextGroup:
            line_print(search_by_context(args.file, context))

    if args.abstractionLayer:
        for abstraction in args.abstractionLayer:
            line_print(search_by_abstraction(args.file, abstraction))

    if args.all:
        line_print(all_components(args.file))


if __name__ == "__main__":
    main(sys.argv[1:])
