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
import subprocess
import grep_adapter
import argparse



def validate(input_jsonnames: str, input_dotfile):
    """
    this script will give you a list of the components and will repeat the components name if there is NO Match
    :param input_jsonnames: A list of the components from the json file seperated by \n
    :param input_dotfile: The dotfile to match
    """

    with open(input_jsonnames, encoding="utf8") as json:
        for component in json:
            component = component.strip('\n')
            arg_strings = grep_adapter.create_grep_arguments(component)
            print(arg_strings)
            for string in arg_strings:
                p = subprocess.Popen("cat " + input_dotfile + " " + string, shell=True, stdout=subprocess.PIPE)
                if len(p.stdout.readline(3)) == 0:
                    print(component)


def main(argv):
    """

    :param argv:
    """
    # inputjson = "apposs_components.txt"
    # inputdot = "task-depends.dot"
    # validate(inputjson, inputdot)

    parser = argparse.ArgumentParser(description="A tool to validate the json file against the dot file")
    parser.add_argument('jsonfile', type=str, metavar='JSONFILE', help="ksonfile that shall be searched.")
    parser.add_argument('dotfile', type=str, metavar='DOTFILE', help="dotfile that shall be searched.")
    args = parser.parse_args()

    if not args.jsonfile or not args.dotfile:
        print("Try 'jsonparser -h' for more information.")
        sys.exit(1)
    else:
        validate(args.jsonfile, args.dotfile)


if __name__ == "__main__":
    main(sys.argv[1:])