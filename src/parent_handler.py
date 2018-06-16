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
import numpy as np

from graph_tool.all import *

from pprint import pprint

import jsonparser
import graph_analyzer

STANDARD_OUT_DICT = "../out/"


def shared_sub_graphs_direct_list(node_compare_list1: list, node_compare_list2: list, head_list1: list, head_list2: list):
    """
    The function takes two lists of lists containing subgraphs that should be checked for overlap with each element of
    the other list. also takes two "head_lists" which have to be the same length as their respective node_compare_list
    and contain identifiers for the subgraphs at the same position as in node_compare_list.
    The function is a helper to call shared_sub_graphs_direct with every element of the first list and the second list.

    :param node_compare_list1: list of lists each containing the node_ids of an individual subgraph.
    :param node_compare_list2: list of lists each containing the node_ids of an individual subgraph.
    :param head_list1: list of identifiers belonging to the head-node of each list in node_compare_list1.
                        Has to have the same order and length as node_compare_list1.
    :param head_list2: list of identifiers belonging to the head-node of each list in node_compare_list2.
                        Has to have the same order and length as node_compare_list2.
    :return: a list of identifier pairs (depending on the head_lists) whose subgraphs are directly overlapping.
    """
    result = []
    for i in range(0, len(node_compare_list1)):
        ncl1_dict = {}
        for node in node_compare_list1[i]:
            ncl1_dict[str(node)] = True

        result_i = shared_sub_graphs_direct(ncl1_dict, node_compare_list2, head_list2)
        for name in result_i:
            result.append((head_list1[i], name))
    return result


def shared_sub_graphs_direct(main_nodes: dict, node_compare_list: list, head_list: list):
    """
    The function takes a dictionary of a subgraph and a list of lists containing other subgraphs.
    It also takes a "head_list" which has to be the same length as node_compare_list and contains identifiers for
    the subgraphs at the same position as in node_compare_list. The function checks whether any of the subgraphs in
    the list shares a node with the subgraph-dictionary and returns a list of identifiers of the overlapping subgraphs.

    :param main_nodes: a dictionary containing True at every node_id of an original graph.
    :param node_compare_list: list of lists each containing the node_ids of an individual subgraph.
    :param head_list: list of identifiers belonging to the head_node of each list in node_compare_list.
                        Has to have the same order and length as node_compare_list.
    :return: a list of identifiers (depending on head_list) whose subgraphs are directly overlapping
            with any of the main_nodes.
    """
    result_list = []
    for i in range(0, len(node_compare_list)):
        compare_nodes = node_compare_list[i]

        is_overlapping = False
        for n in compare_nodes:
            if main_nodes.get(str(n)) is True:
                is_overlapping = True
                break

        if is_overlapping is True:
            result_list.append(head_list[i])

    return result_list


def shared_sub_graphs_indirect(graph: Graph, node_compare_list: list):
    """
    The function takes a graph and a list of lists containing node_ids. It checks which node_ids subgraphs
    are connected either directly or indirectly via other node_id subgraphs. This means two nodes either sharing
    a part of their subgraph or being indirectly connected via other nodes from the node_compare_list.

    :param graph: the graph whose nodes should be checked.
    :param node_compare_list: the nodes to be compared with each other
    :return: a list of lists, each containing all nodes in/directly connected to each other. Each node from
                node_compare_list only appears once.
    """
    # load all subgraphs once
    loaded_nodes = []
    # for i in node_compare_list:
    for i in range(0, len(node_compare_list)):
        vertices = graph_analyzer.collect_subgraph_vertices(graph, int(node_compare_list[i]))
        loaded_nodes.append(vertices)

    overlapping_information = []

    for i in range(0, len(node_compare_list)-1):  # current main node for subgraph-check
        current_node_compare_list = loaded_nodes[(i+1):]
        head_list = node_compare_list[(i+1):]
        main_nodes_vtx = loaded_nodes[i]
        main_nodes = {}
        for vtx in main_nodes_vtx:
            main_nodes[str(vtx)] = True

        overlapping_subgraphs = shared_sub_graphs_direct(main_nodes, current_node_compare_list, head_list)
        overlapping_information.append(overlapping_subgraphs)
        overlapping_information[i].append(node_compare_list[i])

    # by now we got all direct connections of subgraphs. test03.dot would output [['2', '1'], ['3', '2'], ['4', '3']]
    result_list = find_adjacent(overlapping_information, node_compare_list)
    # here we've got all indirect connections. test03.dot would output [['1', '2', '3', '4']]
    return result_list


def find_adjacent(overlapping_information: list, existing_nodes: list):
    """
    Gets a list of directly connected subgraphs and creates the indirect connections.

    :param overlapping_information: a list of lists each containing direct connections betweeen some subgraphs.
    :param existing_nodes: a list containing each existing node once.
    :return: a list of lists each containing all reachable subgraphs with other connected subgraphs in between.
    """
    result_connections = []
    for node in existing_nodes:

        already_checked = False
        for c in result_connections:
            if node in c:
                already_checked = True
                break
        if already_checked is True:
            continue

        connection_list = []
        connection_list.append(node)
        has_changed = True
        while has_changed is True:
            has_changed = False

            for direct_connection in overlapping_information:

                will_be_checked = False
                for n in connection_list:
                    if n in direct_connection:
                        will_be_checked = True
                        break

                if will_be_checked is True:
                    for new_node in direct_connection:
                        if new_node not in connection_list:
                            connection_list.append(new_node)
                            has_changed = True

        result_connections.append(connection_list)
    return result_connections


def validate_children_subgraphs(graph: Graph, parent_dictionary: dict):
    """
    The function takes a graph and the corresponding dictionary containing
    parent names as keys and children ID lists as values
    (as created in find_childnodes) and checks for every parent whether every childrens subgraphs overlap or not.

    :param graph: the graph for which the nodes in the dictionary should be validated
    :param parent_dictionary: a dictionary as created in find_childnodes
    :return: a list filled with one list for each parent whose children are not part of exactly one graph
            (judging by the connection of their subgraphs).
            Each list contains lists of all nodes connected among each other.
            Also at the end of every list regarding one parent, there is a string containing the name of the parent
    """
    results = []
    counter = 1
    for key, node_collection in parent_dictionary.items():

        print("---------------------------------- node_collection "
              "%i of %i (with size %i): %s" % (counter, len(parent_dictionary), len(node_collection), key))
        counter = counter + 1

        connected_graphs = shared_sub_graphs_indirect(graph, node_collection)
        print("For this key there is/are %i different subgraph/s" % len(connected_graphs))
        if len(connected_graphs) != 1:
            for g in connected_graphs:
                print(g)

        if len(connected_graphs) != 1:
            connected_graphs.append(key)
            results.append(connected_graphs)

    # result looks like [[[node1, node2], [node3, node4], "graph1"], [[node5], [node6, node7, node8], "graph2"]]
    return results


def create_parents(graph_filename: str, json_filename: str):
    """
    The function takes the paths to a graph and a json file (in our bmw-json format) and searches the graph
    for all names contained in the json file.
    Afterwards the graph_analyzer is used to each create a parent node "containing" all found child nodes.

    :param graph_filename: the path to the graph to be searched
    :param json_filename: the path to a json file (in our bmw-json format)
    containing all the names for the parent creation
    """

    graph = load_graph(graph_filename)
    parent_dictionary = find_childnodes(graph, json_filename)

    # combine all childnodes of components to a parentnode
    for name, childnodes in parent_dictionary.items():
        graph = graph_analyzer.add_parent(graph, name, childnodes)

    # add domains, contextGroups and abstractionLayers as parents of the components
    domain_list = jsonparser.get_domainlist()
    for domain in domain_list:
        comp_list = jsonparser.search_by_domain(json_filename, domain)
        comp_list_new = []
        for c in comp_list:
            if ("no Match" in c) or ("kein Match" in c):
                continue
            comp_list_new.append(c)
        lis = graph_analyzer.parse_node_values(graph, comp_list_new)
        graph = graph_analyzer.add_parent(graph, domain, lis)

    context_group_list = jsonparser.get_context_groups()
    for context in context_group_list:
        comp_list = jsonparser.search_by_context(json_filename, context)
        comp_list_new = []
        for c in comp_list:
            if ("no Match" in c) or ("kein Match" in c):
                continue
            comp_list_new.append(c)
        lis = graph_analyzer.parse_node_values(graph, comp_list_new)
        graph = graph_analyzer.add_parent(graph, context, lis)

    abstraction_layer_list = jsonparser.get_abstraction_layers()
    for layer in abstraction_layer_list:
        comp_list = jsonparser.search_by_abstraction(json_filename, layer)
        comp_list_new = []
        for c in comp_list:
            if ("no Match" in c) or ("kein Match" in c):
                continue
            comp_list_new.append(c)
        lis = graph_analyzer.parse_node_values(graph, comp_list_new)
        graph = graph_analyzer.add_parent(graph, layer, lis)

    # add one node for domains, context groups and abstraction layers each
    domain_list_ids = graph_analyzer.parse_node_values(graph, domain_list)
    graph = graph_analyzer.add_parent(graph, "DOMAINS", domain_list_ids)

    context_group_ids = graph_analyzer.parse_node_values(graph, context_group_list)
    graph = graph_analyzer.add_parent(graph, "CONTEXT_GROUPS", context_group_ids)

    abstraction_layer_ids = graph_analyzer.parse_node_values(graph, abstraction_layer_list)
    graph = graph_analyzer.add_parent(graph, "ABSTRACTION_LAYERS", abstraction_layer_ids)

    graph_analyzer.export_graph(graph, STANDARD_OUT_DICT + "parent_handler_output")


def find_childnodes(graph: Graph, json_filename: str):
    """
    The function gets a graph and a json filename in our bmw-json format and searches the graph for all component
    names in the json file.
    Those names can have the form "App&CD;Pie" causing a search for nodes containing both the words "App" and "CD"
    and nodes containing "Pie" - just like in the grep_adapter.
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

            # initialize word_result_list with results of the first word
            wrl = graph_analyzer.search_vertices(graph, s_parts[0])
            # change from vertex object to string
            word_result_list = []
            for v in wrl:
                word_result_list.append(str(v))
            # word_result_list = list(set(word_result_list))

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
                        # word_result_list.remove(node)
                        remove_list.append(node)
                for node in remove_list:
                    word_result_list.remove(node)

            # append result to node_collection
            for n in word_result_list:
                if n not in node_collection:
                    node_collection.append(n)

        if len(node_collection) == 0:
            print("there were no results for the search '%s'" % name)
        parent_dictionary[name] = node_collection

    return parent_dictionary


def print_top_level_connections(graph: Graph):
    """
    Gets a graph and searches all Domain/ContextGroup/AbstractionLayer-names
    (which can be created using parent_handler -c).
    The function each checks the connections between every member of those
    and prints the result using print_connection_dict.

    :param graph: The graph to be checked.
    """
    domain_list = jsonparser.get_domainlist()
    context_group_list = jsonparser.get_context_groups()
    abstraction_layer_list = jsonparser.get_abstraction_layers()

    domain_list_new = []
    context_group_list_new = []
    abstraction_layer_list_new = []

    for d in domain_list:
        if ("no Match" in d) or ("kein Match" in d):
            continue
        domain_list_new.append(d)

    for c in context_group_list:
        if ("no Match" in c) or ("kein Match" in c):
            continue
        context_group_list_new.append(c)

    for a in abstraction_layer_list:
        if ("no Match" in a) or ("kein Match" in a):
            continue
        abstraction_layer_list_new.append(a)

    domain_list_ids = graph_analyzer.parse_node_values(graph, domain_list_new)
    context_group_ids = graph_analyzer.parse_node_values(graph, context_group_list_new)
    abstraction_layer_ids = graph_analyzer.parse_node_values(graph, abstraction_layer_list_new)

    domain_subgraphs = []  # length equals amount of domains.
                           # Contains all nodes of one domain and its subgraph at each field.
                           # [[subgraph1],[subgraph2]]
    domain_child_subgraphs = []  # length equals amount of domains.
                                 # Contains a list of lists each containing all children of a domain
                                 # (components) and their complete subgraph at each field.
                                 # [[[copm_subgraph1], [comp_subgraph2]], [[copm_subgraph1], [comp_subgraph2]]]

    context_group_subgraphs = []
    context_group_child_subgraphs = []

    abstraction_layer_subgraphs = []
    abstraction_layer_child_subgraphs = []

    # load vertices
    for d in range(0, len(domain_list_ids)):
        domain_subgraphs.append([domain_list_ids[d]])
        domain_child_subgraphs.append([])
        children = graph.get_out_neighbours(domain_list_ids[d])
        for child in children:
            child_subgraph = graph_analyzer.collect_subgraph_vertices(graph, child)
            for n in child_subgraph:
                domain_subgraphs[d].append(n)
            domain_child_subgraphs[d].append(child_subgraph)

    for c in range(0, len(context_group_ids)):
        context_group_subgraphs.append([context_group_ids[c]])
        context_group_child_subgraphs.append([])
        children = graph.get_out_neighbours(context_group_ids[c])
        for child in children:
            child_subgraph = graph_analyzer.collect_subgraph_vertices(graph, child)
            for n in child_subgraph:
                context_group_subgraphs[c].append(n)
            context_group_child_subgraphs[c].append(child_subgraph)

    for a in range(0, len(abstraction_layer_ids)):
        abstraction_layer_subgraphs.append([abstraction_layer_ids[a]])
        abstraction_layer_child_subgraphs.append([])
        children = graph.get_out_neighbours(abstraction_layer_ids[a])
        for child in children:
            child_subgraph = graph_analyzer.collect_subgraph_vertices(graph, child)
            for n in child_subgraph:
                abstraction_layer_subgraphs[a].append(n)
            abstraction_layer_child_subgraphs[a].append(child_subgraph)

    domain_dict_all_collisions = {}
    domain_dict_component_collisions = {}

    context_dict_all_collisions = {}
    context_dict_component_collisions = {}

    abstraction_dict_all_collisions = {}
    abstraction_dict_component_collisions = {}

    # compare subgraphs
    for i in range(0, len(domain_list_ids)):
        print("currently checking Domains at position %i of %i (%s)" % (i, len(domain_list_ids)-1, domain_list_new[i]))
        domain_dict_all_collisions[domain_list_new[i]] = []
        domain_dict_component_collisions[domain_list_new[i]] = []

        for j in range(0, len(domain_list_ids)):
            subcollisions = 0           # count all subcollisions
            component_collisions = 0    # count all collisions of components
            if i == j:
                subcollisions = -1
                component_collisions = -1
            else:
                subcollision_list = graph_analyzer.list_shared_sub_vertices(graph, domain_list_ids[i], domain_list_ids[j])
                subcollisions = len(subcollision_list)

                component_subcollision_list = shared_sub_graphs_direct_list(domain_child_subgraphs[i],
                                                                            domain_child_subgraphs[j],
                                                                            domain_child_subgraphs[i],
                                                                            domain_child_subgraphs[j])
                component_collisions = len(component_subcollision_list)

            # append to solution
            subcollisions_pair = (domain_list_new[j], subcollisions)
            domain_dict_all_collisions[domain_list_new[i]].append(subcollisions_pair)

            component_collisions_pair = (domain_list_new[j], component_collisions)
            domain_dict_component_collisions[domain_list_new[i]].append(component_collisions_pair)

    print("Domains done.")

    for i in range(0, len(context_group_ids)):
        print("currently checking Context Groups at position %i of %i (%s)" %
                                                            (i, len(context_group_ids) - 1, context_group_list_new[i]))
        context_dict_all_collisions[context_group_list_new[i]] = []
        context_dict_component_collisions[context_group_list_new[i]] = []

        for j in range(0, len(context_group_ids)):
            subcollisions = 0  # count all subcollisions
            component_collisions = 0  # count all collisions of components
            if i == j:
                subcollisions = -1
                component_collisions = -1
            else:
                subcollision_list = graph_analyzer.list_shared_sub_vertices(graph, context_group_ids[i], context_group_ids[j])
                subcollisions = len(subcollision_list)

                component_subcollision_list = shared_sub_graphs_direct_list(context_group_child_subgraphs[i],
                                                                            context_group_child_subgraphs[j],
                                                                            context_group_child_subgraphs[i],
                                                                            context_group_child_subgraphs[j])
                component_collisions = len(component_subcollision_list)

            # append to solution
            subcollisions_pair = (context_group_list_new[j], subcollisions)
            context_dict_all_collisions[context_group_list_new[i]].append(subcollisions_pair)

            component_collisions_pair = (context_group_list_new[j], component_collisions)
            context_dict_component_collisions[context_group_list_new[i]].append(component_collisions_pair)

    print("Context Groups done.")

    for i in range(0, len(abstraction_layer_ids)):
        print("currently checking Abstraction Layers at position %i of %i (%s)" %
                                                        (i, len(abstraction_layer_ids) - 1, abstraction_layer_list_new[i]))
        abstraction_dict_all_collisions[abstraction_layer_list_new[i]] = []
        abstraction_dict_component_collisions[abstraction_layer_list_new[i]] = []

        for j in range(0, len(abstraction_layer_ids)):
            subcollisions = 0  # count all subcollisions
            component_collisions = 0  # count all collisions of components
            if i == j:
                subcollisions = -1
                component_collisions = -1
            else:
                subcollision_list = graph_analyzer.list_shared_sub_vertices(graph, abstraction_layer_ids[i], abstraction_layer_ids[j])
                subcollisions = len(subcollision_list)

                component_subcollision_list = shared_sub_graphs_direct_list(abstraction_layer_child_subgraphs[i],
                                                                            abstraction_layer_child_subgraphs[j],
                                                                            abstraction_layer_child_subgraphs[i],
                                                                            abstraction_layer_child_subgraphs[j])
                component_collisions = len(component_subcollision_list)

            # append to solution
            subcollisions_pair = (abstraction_layer_list_new[j], subcollisions)
            abstraction_dict_all_collisions[abstraction_layer_list_new[i]].append(subcollisions_pair)

            component_collisions_pair = (abstraction_layer_list_new[j], component_collisions)
            abstraction_dict_component_collisions[abstraction_layer_list_new[i]].append(component_collisions_pair)

    print("Abstraction Layers done. Now writing output.")

    print_connection_dict_advanced(domain_dict_all_collisions, STANDARD_OUT_DICT + "domain.csv")
    print_connection_dict_advanced(domain_dict_component_collisions, STANDARD_OUT_DICT + "domain_component_collisions.csv")

    print_connection_dict_advanced(context_dict_all_collisions, STANDARD_OUT_DICT + "context.csv")
    print_connection_dict_advanced(context_dict_component_collisions, STANDARD_OUT_DICT + "context_component_collisions.csv")

    print_connection_dict_advanced(abstraction_dict_all_collisions, STANDARD_OUT_DICT + "abstraction.csv")
    print_connection_dict_advanced(abstraction_dict_component_collisions, STANDARD_OUT_DICT + "abstraction_component_collisions.csv")


def print_connection_dict(d: dict, file_name: str):
    """
    Gets a dictionary with Domain/ContextGroup/AbstractionLayer-names as keys and a list with all the
    Domains/ContextGroups/AbstractionLayers they overlap with as values. Prints stuff to command line / file.

    :param d: A dictionary containing overlapping information.
    :param file_name: the name of the output file.
    """
    output_array = np.zeros((len(d), len(d)))
    i = 0
    key_list = list(d.keys())
    for key, value in d.items():
        for name in value:
            j = key_list.index(name)
            output_array[i][j] = 1
        i = i + 1
    np.savetxt(file_name, output_array, delimiter=",", fmt="%.0f")
    print(output_array)

    with open(STANDARD_OUT_DICT+file_name, "a", encoding="utf-8") as outfile:
        outfile.write("\n")
        s = '{}, '.format(map(str, key_list))
        outfile.write(s)


def print_connection_dict_advanced(d: dict, file_name: str):
    """
    Gets a dictionary with Domain/ContextGroup/AbstractionLayer-names as keys and a list with all the
    Domains/ContextGroups/AbstractionLayers they overlap with as values. Prints stuff to command line / file.

    :param d: A dictionary containing advanced overlapping information.
    :param file_name: the name of the output file.
    """
    output_array = np.zeros((len(d), len(d)))
    i = 0
    key_list = list(d.keys())
    for key, value in d.items():
        for name_count_pair in value:
            name, count = name_count_pair
            j = key_list.index(name)
            output_array[i][j] = count
        i = i + 1
    np.savetxt(file_name, output_array, delimiter=",", fmt="%.0f")
    print(output_array)
    print("")
    print(key_list)
    print("")
    print("")
    with open(STANDARD_OUT_DICT+file_name, "a", encoding="utf-8") as outfile:
        outfile.write("\n")
        s = ', '.join(map(str, key_list))
        outfile.write(s)


def main(argv):
    """
    Main function which parses the passed arguments.

    :param argv: the argument list passed by the command line
    """
    parser = argparse.ArgumentParser(
        description="A script to search a graph for all nodes mentioned in a json file (in our bmw-json format). "
                    "Those nodes are then each combined into a parent node and the resulting graph is then outputted "
                    "in another file. "
                    "This has to be called from withing our src folder as it uses the jsonparser and graph_analyzer. "
                    "Another service is the validation of parent nodes. This checks whether all children are somehow "
                    "connected to eac other. "
                    "For testing you can also call this with test03.dot and test03.json.")
    parser.add_argument('file1', type=str, metavar='GRAPH_FILE', help=".dot or .gt file containing a graph.")
    parser.add_argument('-j', '--json_file', type=str, metavar='JSON_FILE', help=".json file containing node names.")
    parser.add_argument('-c', '--createParents', action='store_true',
                        help="Create parents according to the json file.")
    parser.add_argument('-v', '--validate', action='store_true',
                        help="Validate connection of the children in the json file.")
    parser.add_argument('-p', '--print_top_level_connections', action='store_true',
                        help="Prints Connections between domains & co. and which nodes cause them.")
    args = parser.parse_args()

    if not args.file1:
        print("Try 'parent_handler -h' for more information.")
        sys.exit(1)

    if args.createParents:
        if not args.json_file:
            print("Try 'parent_handler -h' for more information.")
            sys.exit(1)
        create_parents(args.file1, args.json_file)
        return

    if args.validate:
        if not args.json_file:
            print("Try 'parent_handler -h' for more information.")
            sys.exit(1)
        graph = load_graph(args.file1)
        print("find_childnodes has begun")
        parent_dict = find_childnodes(graph, args.json_file)
        print("validation has begun")
        trouble_list = validate_children_subgraphs(graph, parent_dict)
        if len(trouble_list) != 0:
            # print on command line
            print("the following nodes and their subgraphs aren't connected even though they share the same parent:")
            for graph in trouble_list:
                print(graph[len(graph)-1] + ":")
                for i in range(0, len(graph)-1):
                    print(graph[i])
                print("")

            # write to file
            with open(STANDARD_OUT_DICT + "parent_handler_validation.txt", "w", encoding="utf-8") as file:
                for graph in trouble_list:
                    file.write(graph[len(graph)-1] + "\n")
                    lists = graph[0:len(graph) - 1]
                    for lis in lists:
                        file.write(lis[0])
                        for i in range(1, len(lis)):
                            file.write(",")
                            file.write(lis[i])
                        file.write("\n")
                    file.write("\n")

        else:
            print("Everything is fine. All nodes with the same parent are somewhere connected within their subgraphs")
        return

    if args.print_top_level_connections:
        graph = load_graph(args.file1)
        print_top_level_connections(graph)
        return


if __name__ == "__main__":
    main(sys.argv[1:])
