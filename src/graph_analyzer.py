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

from graph_tool.all import *

import sys
import getopt


def print_graph_vertices(file_name):
    """
    Prints some information about the vertices in a graph. Only used for experiments and debugging.

    :param file_name: the path to the file corresponding *.dot file
    """
    graph = load_graph(file_name)

    # print vertices values
    dict_size = 0
    for vtx in graph.properties[("v", "vertex_name")]:
        print(vtx)
        dict_size = dict_size + 1

    # print detailed vertex data
    for i in range(0, dict_size):
        vtx = graph.vertex(i)
        print("vertex:", int(vtx),
              "in-degree:", vtx.in_degree(),
              "out-degree:", vtx.out_degree(),
              "value:", graph.vp.vertex_name[vtx])


def main(argv):
    """
    Main function which parses the passed arguments.

    :param argv: the argument list passed by the command line
    """

    DEBUG_FILE = "../tests/test01.dot"
    INVALID_INPUT_MSG = "graph_analyzer: invalid input --"
    ARG_ERROR_MSG = "Try 'graph_analyzer -h' for more information."
    HELP_MSG = """Usage: graph_analyzer [OPTION ...] FILE
              Options:
              -h, -?, --help         Print this message.
              -s, --search <NODE>    Searches for the given node."""

    def print_arg_error_and_exit():
        print(ARG_ERROR_MSG)
        sys.exit(1)

    file_name = DEBUG_FILE  # file_name could be predefined here (e.g. for testing)
    try:
        opts, args = getopt.getopt(argv, "h?s:", ["help", "search="])
    except getopt.GetoptError as err:
        print(INVALID_INPUT_MSG, err)
        print_arg_error_and_exit()

    for opt, arg in opts:
        if opt in ("-h", "-?", "--help"):
            print(HELP_MSG)
            sys.exit()
        elif opt in ("-s", "--search"):
            print("Search results for", arg)
            # TODO: implement search function
        else:
            print(INVALID_INPUT_MSG, opt)
            print_arg_error_and_exit()

    if not args:
        if not file_name:
            print("No input file.")
            print_arg_error_and_exit()
    else:
        file_name = args[0]

    print_graph_vertices(file_name)


if __name__ == "__main__":
    main(sys.argv[1:])