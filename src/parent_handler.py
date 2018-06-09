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

STANDARD_OUT_DICT="../out/"


def validate_children_subgraphs(graph: Graph, parent_dictionary: dict):
    """
    The function takes a graph and the corresponding dictionary containing parent names as keys and children ID lists as values
    (as created in find_childnodes) and checks for every parent whether every childrens subgraphs overlap or not.

    :param graph_in: the graph or its filename for which the nodes in the dictionary should be validated
    :param parent_dictionary: a dictionary as created in find_childnodes
    :return: a list filled with tuples of children whose subgraphs do not overlap or an empty list if every subgraph overlaps any other
    """
    results = []
    debug_counter = 1
    for key, node_collection in parent_dictionary.items():

        if(debug_counter > 5):
            break

        print("----------------------------------node_collection %i of %i: %s" % (debug_counter, len(parent_dictionary), key))
        debug_counter = debug_counter + 1

        for i in range(0, len(node_collection)):

            print("i = %i, max = %i" % (i, len(node_collection)))

            for j in range(i+1, len(node_collection)):
                shared_subgraphs = graph_analyzer.list_shared_sub_vertices(graph, int(node_collection[i]), int(node_collection[j]))
                if(len(shared_subgraphs) == 0):
                    l = [node_collection[i], node_collection[j]]
                    results.append(l)

    return results


def create_parents(graph_filename: str, json_filename: str):
    """
    The function takes the paths to a graph and a json file (in our bmw-json format) and searches the graph for all names contained in the json file.
    Afterwards the graph_analyzer is used to each create a parent node "containing" all found child nodes.

    :param graph_filename: the path to the graph to be searched
    :param json_filename: the path to a json file (in our bmw-json format) containing all the names for the parent creation
    """

    graph = load_graph(graph_filename)
    parent_dictionary = find_childnodes(graph, json_filename)

    # combine all childnodes to a parentnode
    for name,childnodes in parent_dictionary.items():
        graph = graph_analyzer.add_parent(graph, name, childnodes)
    graph_analyzer.export_graph(graph, STANDARD_OUT_DICT + "parent_handler_output")


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
    debugcounter = 0
    all_names = jsonparser.all_components(json_filename)
    for name in all_names:
        if ("kein Match" in name) or ("no Match" in name):
            continue

        if(debugcounter > 5):
            break
        debugcounter = debugcounter + 1

        search_names = name.split(";")
        node_collection = []
        for s_name in search_names:
            s_parts = s_name.split("&")
            # search for nodes containing every word in s_parts

            #initialize word_result_list with results of the first word
            wrl = graph_analyzer.search_vertices(graph, s_parts[0])
            # change from vertex object to string
            word_result_list = []
            for v in wrl:
                word_result_list.append(str(v))
            #word_result_list = list(set(word_result_list))

            for word in s_parts:
                nl = graph_analyzer.search_vertices(graph, word)
                # change from vertex object to string
                node_list = []
                for v in nl:
                    node_list.append(str(v))
                #node_list = list(set(node_list))

                #if name == "lib&coding":
                #    print("nodelist: %i" % len(node_list))

                # remove nodes from word_result_list that are not in node_list
                remove_list = []
                for node in word_result_list:
                    if node not in node_list:
                        #word_result_list.remove(node)
                        remove_list.append(node)
                for node in remove_list:
                    word_result_list.remove(node)

            #if name == "lib&coding":
            #    print(len(word_result_list))

            # append result to node_collection
            for n in word_result_list:
                if n not in node_collection:
                    node_collection.append(n)

        if(len(node_collection) == 0):
            print("there were no results for the search '%s'" % name)
        parent_dictionary[name] = node_collection

    return parent_dictionary


def main(argv):
    """
    Main function which parses the passed arguments.

    :param argv: the argument list passed by the command line
    """
    parser = argparse.ArgumentParser(description="A script to search a graph for all nodes mentioned in a json file (in our bmw-json format). "
                                                 "Those nodes are then each combined into a parent node and the resulting graph is then outputted in another file. "
                                                 "This has to be called from withing our src folder as it uses the jsonparser and graph_analyzer")
    parser.add_argument('file1', type=str, metavar='GRAPH_FILE', help=".dot or .gt file containing a graph.")
    parser.add_argument('file2', type=str, metavar='JSON_FILE', help=".json file containing node names.")
    parser.add_argument('-c', '--createParents', action='store_true',
                        help="Create parents according to the json file.")
    parser.add_argument('-v', '--validate', action='store_true',
                        help="Validate connection of the children in the json file. This takes a LONG time.")
    args = parser.parse_args()

    if not args.file1 or not args.file2:
        print("Try 'parent_handler -h' for more information.")
        sys.exit(1)

    if args.createParents:
        create_parents(args.file1, args.file2)
        return

    if args.validate:
        graph = load_graph(args.file1)
        print("find_childnodes has begun")
        parent_dict = find_childnodes(graph, args.file2)
        print("parentdict:")
        pprint(parent_dict)
        print("validation has begun")
        trouble_list = validate_children_subgraphs(graph, parent_dict)
        if (len(trouble_list) != 0):
            print("the following nodes and their subgraphs aren't connected even though they share the same parent:")
            pprint(trouble_list)
            file = open(STANDARD_OUT_DICT + "parent_handler_validation.txt", "w")
            for item in trouble_list:
                #print("%s, %s" % (item[0][0], item[0][1]))
                file.write(item[0] + ", " + item[1] + "\n")
        else:
            print("Everything is fine. All nodes with the same parent are somewhere connected within their subgraphs")
        return


if __name__ == "__main__":
    main(sys.argv[1:])
