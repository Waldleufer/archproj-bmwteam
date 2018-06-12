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

import argparse
import json
import sys


def write_list_with_same_groups(json_file: str, component_list: str, domain: str,
                                context_group: str, hardware_group: str):
    """
    appends a List of components to the json_file that have the same domain,
    the same context_group and the same hardwareGroup

    :param json_file: name of file where to add the names as string
    :param component_list: File with \n separated component names to add
    :param domain: domain that shall be applied to all items of component_list
    :param context_group: contextGroup of all items
    :param hardware_group: hardwareGroup of all items
    """
    with open(json_file, "w") as write_file:

        components = map(str.strip, open(component_list).readlines())

        data_list = list()

        for component in components:

            comp = {
                component: {
                    "domain": domain,
                    "contextGroup": context_group,
                    "hardwareGroup": hardware_group
                }
            }
            data_list.append(comp)
        write_file.write(json.dumps(data_list, indent=2))


def main(argv):
    """
        runs the script from the command line
    """

    parser = argparse.ArgumentParser(description="A tool to semi automatically create formatted sections according "
                                                 "to bmwSoftwareArchitecture_archproj-bmwteam-schema.json")
    parser.add_argument('json_file', type=str, metavar='OUTPUT_FILE', help="Output file that will be overwritten")
    parser.add_argument('component_list', type=str, metavar='COMPONENT_LIST_FILE',
                        help="A '\\n' separated list of all components that shall have the same "
                             "domain context- and hardwareGroup afterwards")
    parser.add_argument('domain', type=str, metavar='domain',
                        help="the name of the domain")
    parser.add_argument('context', type=str, metavar='contextGroup',
                        help="the name of the contextGroup")
    parser.add_argument('hardware', type=str, metavar='hardwareGroup',
                        help="the name of the hardwareGroup")
    args = parser.parse_args()

    if not args.json_file or not args.component_list or not args.domain or not args.context or not args.hardware:
        print("Try 'bmwArchitecture_to_json -h' for more information.")
        sys.exit(1)
    else:
        write_list_with_same_groups(args.json_file, args.component_list, args.domain, args.context, args.hardware)


if __name__ == "__main__":
    main(sys.argv[1:])
