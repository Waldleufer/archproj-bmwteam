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


def shared_sub_graphs_direct(graph: Graph, main_nodes: dict, node_compare_list: list, head_list: list):
    """
    :param graph: the graph whose nodes should be checked.
    :param main_nodes: a dictionary containing True at every node_id of an original graph.
    :param node_compare_list: list of lists each containing the node_ids of a individual subgraph
    :return: a list of node_ids whose subgraphs are directly overlapping with any of the main_nodes
    """
    result_list = []
    #for compare_nodes_parent in node_compare_list:
    for i in range(0,len(node_compare_list)):
        compare_nodes = node_compare_list[i]

        is_overlapping = False
        for n in compare_nodes:
            if (main_nodes.get(str(n)) == True):
                is_overlapping = True
                break

        if(is_overlapping == True):
            result_list.append(head_list[i])

    return result_list


def shared_sub_graphs_indirect(graph: Graph, node_compare_list: list):
    """
    The function takes a graph and a node_id thereof, checking whether the node is somehow connected via subgraphs to
    the nodes in the node_node_compare_list. This includes two nodes sharing a part of their subgraph as well as
    being indirectly connected via other nodes from the node_compare_list.

    :param graph: the graph whose nodes should be checked.
    :param main_node_id: the node which should be compared to other nodes from the node_compare_list
    :param node_compare_list: the nodes to be compared with the given node_id
    :return: a list of node_ids containing every node NOT connected to the input node_id
    """
    # load all subgraphs once
    loaded_nodes = []
    #for i in node_compare_list:
    for i in range(0, len(node_compare_list)):
        vertices = graph_analyzer.collect_subgraph_vertices(graph, int(node_compare_list[i]))
        loaded_nodes.append(vertices)

    overlapping_information = []

    for i in range(0,len(node_compare_list)-1): # current main node for subgraph-check
        current_node_compare_list = loaded_nodes[(i+1):]
        head_list = node_compare_list[(i+1):]
        main_nodes_vtx = loaded_nodes[i]
        main_nodes = {}
        for vtx in main_nodes_vtx:
            main_nodes[str(vtx)] = True

        overlapping_subgraphs = shared_sub_graphs_direct(graph, main_nodes, current_node_compare_list, head_list)
        overlapping_information.append(overlapping_subgraphs)
        overlapping_information[i].append(node_compare_list[i])

    #by now we got all direct connections of subgraphs. test03.dot would output [['2', '1'], ['3', '2'], ['4', '3']]
    result_list = find_adjacent(overlapping_information, node_compare_list)
    #here we've got all indirect connections. test03.dot would output [['1', '2', '3', '4']]
    return result_list


def find_adjacent(overlapping_information: list, existing_nodes: list):
    """
    Gets a list of directly connected subgraphs and adds the indirect connections.

    :param overlapping_information: a list of lists each containing direct connections betweeen some subgraphs.
    :param existing_nodes: a list containing each existing node once.
    :return: a list of lists each containing all reachable subgraphs with other connected subgraphs in between.
    """
    result_connections = []
    for node in existing_nodes:

        already_checked = False
        for c in result_connections:
            if(node in c):
                already_checked = True
                break
        if(already_checked == True):
            continue

        connection_list = []
        connection_list.append(node)
        has_changed = True
        while (has_changed == True):
            has_changed = False

            for direct_connection in overlapping_information:

                will_be_checked = False
                for n in connection_list:
                    if n in direct_connection:
                        will_be_checked = True
                        break

                if(will_be_checked == True):
                    for new_node in direct_connection:
                        if new_node not in connection_list:
                            connection_list.append(new_node)
                            has_changed = True

        result_connections.append(connection_list)
    return result_connections



def validate_children_subgraphs(graph: Graph, parent_dictionary: dict):
    """
    The function takes a graph and the corresponding dictionary containing parent names as keys and children ID lists as values
    (as created in find_childnodes) and checks for every parent whether every childrens subgraphs overlap or not.

    :param graph: the graph for which the nodes in the dictionary should be validated
    :param parent_dictionary: a dictionary as created in find_childnodes
    :return: a list filled with one list for each parent whose children are not part of exactly one graph
            (judging by the connection of their subgraphs). Each list contains lists of all nodes connected among each other.
            Also at the end of every list regarding one parent, there is a string containing the name of the parent
    """
    results = []
    counter = 1
    for key, node_collection in parent_dictionary.items():

        print("----------------------------------node_collection %i of %i (with size %i): %s" % (counter, len(parent_dictionary), len(node_collection), key))
        counter = counter + 1

        connected_graphs = shared_sub_graphs_indirect(graph, node_collection)
        print("For this key there is/are %i different subgraph/s" % len(connected_graphs))
        if(len(connected_graphs) != 1):
            for g in connected_graphs:
                print(g)

        if(len(connected_graphs) != 1):
            connected_graphs.append(key)
            results.append(connected_graphs)

    #result looks like [[[node1, node2], [node3, node4], "graph1"], [[node5], [node6, node7, node8], "graph2"]]
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
    all_names = jsonparser.all_components(json_filename)
    for name in all_names:
        if ("kein Match" in name) or ("no Match" in name):
            continue

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

                # remove nodes from word_result_list that are not in node_list
                remove_list = []
                for node in word_result_list:
                    if node not in node_list:
                        #word_result_list.remove(node)
                        remove_list.append(node)
                for node in remove_list:
                    word_result_list.remove(node)

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
                                                 "This has to be called from withing our src folder as it uses the jsonparser and graph_analyzer."
                                                 "For testing you can also call this with test03.dot and test03.json.")
    parser.add_argument('file1', type=str, metavar='GRAPH_FILE', help=".dot or .gt file containing a graph.")
    parser.add_argument('file2', type=str, metavar='JSON_FILE', help=".json file containing node names.")
    parser.add_argument('-c', '--createParents', action='store_true',
                        help="Create parents according to the json file.")
    parser.add_argument('-v', '--validate', action='store_true',
                        help="Validate connection of the children in the json file.")
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
        print("validation has begun")
        trouble_list = validate_children_subgraphs(graph, parent_dict)
        if (len(trouble_list) != 0):
            # print on command line
            print("the following nodes and their subgraphs aren't connected even though they share the same parent:")
            for graph in trouble_list:
                print(graph[len(graph)-1] + ":")
                for i in range(0, len(graph)-1):
                    print(graph[i])
                print("")

            # write to file
            file = open(STANDARD_OUT_DICT + "parent_handler_validation.txt", "w")
            for graph in trouble_list:
                file.write(graph[len(graph)-1] + ":\n")
                lists = graph[0:len(graph) - 1]
                for lis in lists:
                    for i in range(0, len(graph)-1):
                        file.write(lis[i])
                        file.write(",")
                    file.write(lis[len(lis) - 1])
                    file.write("\n")
                file.write("\n")

        else:
            print("Everything is fine. All nodes with the same parent are somewhere connected within their subgraphs")
        return


if __name__ == "__main__":
    main(sys.argv[1:])
