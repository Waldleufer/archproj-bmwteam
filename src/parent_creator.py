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
import argparse
from graph_tool.all import *

from pprint import pprint

import jsonparser
import graph_analyzer

STANDARD_OUT_NAME="parent_creator_output"


def create_parents(graph_filename: str, json_filename: str, out_filename: str):
    """
    The function takes the paths to a graph and a json file (in our bmw-json format) and searches the graph for all names contained in the json file.
    Afterwards the graph_analyzer is used to each create a parent node "containing" all found child nodes.

    :param graph_filename: the path to the graph to be searched
    :param json_filename: the path to a json file (in our bmw-json format) containing all the names for the parent creation
    """

    out_string = "../out/" + out_filename



    graph = load_graph(graph_filename)
    parent_dictionary = find_childnodes(graph, json_filename)

    # combine all childnodes to a parentnode
    for name,childnodes in parent_dictionary.items():
        graph = graph_analyzer.add_parent(graph, name, childnodes)
    graph_analyzer.export_graph(graph, out_string)




def find_childnodes(graph: Graph, json_filename: str):
    """
    The function gets a graph and a json filename in our bmw-json format and searches the graph for all component names in the json file.
    Those names can have the form "App&CD;Pie" causing a search for nodes containing both the words "App" and "CD" and nodes containing "Pie" - just like in the grep_adapter.
    The nodes are then listed in a dictionary with the original name from the json file as the key.
    This dictionary is then retured.

    :param graph: the graph to be searched
    :param json_filename: the path to a json file (in our bmw-json format) containing all the names for the search
    :return: a dictionary with names from the json file as keys and all found nodes in a list as value
    """
    parent_dictionary = {}

    all_names = jsonparser.all_components(json_filename)
    for name in all_names:
        if ("kein Match" in name) or ("no Match" in name):
            continue

        search_names = name.split(";")
        node_collection = []
        for s_name in search_names:
            s_parts = s_name.split("&")
            # search for nodes containing every word in s_parts
            wrl = graph_analyzer.search_vertices(graph, s_parts[0])
            # change from vertex object to string
            word_result_list = []
            for v in wrl:
                word_result_list.append(str(v))

            for word in s_parts:
                nl = graph_analyzer.search_vertices(graph, word)
                # change from vertex object to string
                node_list = []
                for v in nl:
                    node_list.append(str(v))

                for node in word_result_list:
                    # remove nodes from word_result_list that are not in node_list
                    if node not in node_list:
                        word_result_list.remove(node)

            # append result to node_collection
            for n in word_result_list:
                if n not in node_collection:
                    node_collection.append(n)
        parent_dictionary[name] = node_collection

    # check if any node_collection collides with another
    troublemaker_keys = []
    for key,node_collection in parent_dictionary.items():
        for k,nc in parent_dictionary.items():
            if key is k:
                continue

            for node in node_collection:
                if node in nc:
                    if key not in troublemaker_keys:
                        troublemaker_keys.append(key)
                    if k not in troublemaker_keys:
                        troublemaker_keys.append(k)
    if len(troublemaker_keys) != 0:
        print("The following keys are part of collisions:")
        pprint(troublemaker_keys)

    return parent_dictionary






def main(argv):
    """
    Main function which parses the passed arguments.

    :param argv: the argument list passed by the command line
    """
    parser = argparse.ArgumentParser(description="A script to search a graph for all nodes mentioned in a json file (in our bmw-json format). "
                                                 "Those nodes are then each combined into a parent node and the resulting graph is then outputted in another file. "
                                                 "This has to be called from withing our src folder as it uses the jsonparser and graph_analyzer")
    parser.add_argument('file1', type=str, metavar='FILE', help=".dot or .gt file containing a graph.")
    parser.add_argument('file2', type=str, metavar='FILE', help=".json file containing node names.")
    parser.add_argument('-o', '--out', type=str, nargs=1, metavar='FILE-NAME',
                        help="Set a specific file name for an exported *.gt-file.")
    args = parser.parse_args()

    if not args.file1 or not args.file2:
        print("Try 'parent_creator -h' for more information.")
        sys.exit(1)

    if args.out:
        create_parents(args.file1, args.file2, args.out)
    else:
        create_parents(args.file1, args.file2, STANDARD_OUT_NAME)


if __name__ == "__main__":
    main(sys.argv[1:])
