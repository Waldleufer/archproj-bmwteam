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


def print_graph_vertices(graph: Graph):
    """
    Prints some information about the vertices in the given graph.
    'in-degree': The number of edges to parent nodes.
    'out-degree': The number of edges to child nodes.
    'value': The name of the node.

    :param graph: the graph to print
    """
    # print detailed vertex data
    for vtx in graph.vertices():
        print("vertex[%d]" % vtx,
              "in-degree:", vtx.in_degree(),
              ", out-degree:", vtx.out_degree(),
              ", value:", graph.vp.vertex_name[vtx])


def search_vertices(graph: Graph, search_str: str) -> list:
    """
    Searches for nodes which contain the given search string (case sensitive).

    :param graph: the graph containing the nodes
    :param search_str: the string to search for in the node name
    :return: a list of the found vertices or a empty list
    """
    vtx_list = []
    for vtx in graph.vertices():
        vtx_value = graph.vp.vertex_name[vtx]
        if vtx_value.find(search_str) != -1:
            vtx_list.append(vtx)
    return vtx_list


def main(argv):
    """
    Main function which parses the passed arguments.

    :param argv: the argument list passed by the command line
    """

    DEBUG_FILE = "../tests/test01.dot"  # TODO: remove on release
    INVALID_INPUT_MSG = "graph_analyzer: invalid input --"
    ARG_ERROR_MSG = "Try 'graph_analyzer -h' for more information."
    HELP_MSG = """Usage: graph_analyzer [OPTION ...] FILE
              Options:
              -h, -?, --help         Print this message.
              -p, --print            Print all nodes and their details.
              -s, --search <NODE>    Searches for the given node."""

    def print_arg_error_and_exit():
        print(ARG_ERROR_MSG)
        sys.exit(1)

    file_name = DEBUG_FILE  # file_name could be predefined here (e.g. for testing)
    try:
        opts, args = getopt.getopt(argv, "h?ps:", ["help", "print", "search="])
    except getopt.GetoptError as err:
        print(INVALID_INPUT_MSG, err)
        print_arg_error_and_exit()

    if not args:
        if not file_name:
            print("No input file.")
            print_arg_error_and_exit()
    else:
        file_name = args[0]

    graph = load_graph(file_name)

    for opt, arg in opts:
        if opt in ("-h", "-?", "--help"):
            print(HELP_MSG)
            sys.exit()
        elif opt in ("-p", "--print"):
            print_graph_vertices(graph)
        elif opt in ("-s", "--search"):
            print("Search results for '%s':" % arg)
            vertex_list = search_vertices(graph, arg)
            if len(vertex_list) > 0:
                for vtx in vertex_list:
                    vtx_value = graph.vp.vertex_name[vtx]
                    print("vertex[%s]" % int(vtx), vtx_value)
            else:
                    print("Nothing found.")
        else:
            print(INVALID_INPUT_MSG, opt)
            print_arg_error_and_exit()


if __name__ == "__main__":
    main(sys.argv[1:])
