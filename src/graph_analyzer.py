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

    file_name = "../tests/test01.dot"  # file_name could be predefined here (e.g. for testing)
    try:
        opts, args = getopt.getopt(argv, "h?", ["help"])
    except getopt.GetoptError:
        print("graph-analyzer.py <file_name>")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "-?", "--help"):
            print("Usage: graph-analyzer.py [ options ... ] [file_name]\n\n"
                  "Options:\n"
                  "-h, -?, --help\t Print this message.")
            sys.exit()

    if not args:
        if not file_name:
            print("graph-analyzer.py <file_name>")
            sys.exit(2)
    else:
        file_name = args[0]

    print_graph_vertices(file_name)


if __name__ == "__main__":
    main(sys.argv[1:])