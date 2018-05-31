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
import sys
import os


DEFAULT_OUTPUT_DIR = "../out/"


def create_grep_argument(search_str: str):
    """
    creates a executable comand line argument from a given input string with the format word1[;word2[;wordn]]
    intended useage is cat Inputfile X
    where X is the argument created by this adapter.
    the search is case insensitive

    :type search_str: str
    :param search_str: the string in the upperhand specified format
    :return the list with all ready-to-be-parsed strings
    """
    pre = ""
    out = list()
    words = search_str.split(";")
    for wdiff in words:
        split = wdiff.split("&")
        for wunion in split:
            pre += '| grep -i "' + wunion + '" '
        out.append(pre)

    return out


def main(argv):
    """
    Main function which parses the passed arguments.

    :param argv: the argument list passed by the command line
    """
    parser = argparse.ArgumentParser(description="A adapter to search for a component from the json file")
    parser.add_argument('file', type=str, metavar='FILE', help="Search for the given string.")
    parser.add_argument('searchstring', type=str, metavar='SEARCH_STR', help='Search for the given string.')
    args = parser.parse_args()

    if (not args.file) or (not args.searchstring):
        print("Try 'graph_analyzer -h' for more information.")
        sys.exit(1)
    else:
        exec_strings = create_grep_argument(args.searchstring)
        s: str
        for s in exec_strings:
            os.system("cat " + args.file + " " + s)


if __name__ == "__main__":
    main(sys.argv[1:])
