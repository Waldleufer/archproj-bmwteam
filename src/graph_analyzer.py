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
from time import gmtime, strftime
from enum import Enum
from utils.unconnected_graphs import UnconnectedGraphs

import argparse
import sys
import math
import os
import itertools

DEFAULT_OUTPUT_DIR = "../out/"
HELP_INFO_MSG = "Try 'graph_analyzer -h' for more information."


def print_graph_vertex(graph: Graph, vertex: int):
    """
    Prints some information about the given node (a.k.a. vertex).
    'in-degree': The number of edges to parent nodes.
    'out-degree': The number of edges to child nodes.
    'value': The name of the node.

    :param graph: the graph to print
    :param vertex: optional list of vertices to print out
    """
    print("vtx[%s]" % vertex,
          "in:", graph.vertex(vertex).in_degree(),
          "out:", graph.vertex(vertex).out_degree(),
          "val:", graph.vp.vertex_name[vertex])


def print_vertex_children(graph: Graph, vertex: int, degree=1):
    """
    Prints the given vertex and all its (sub-)children in a tree-like structure.

    :param graph: the graph which contains the given vertex
    :param vertex: the vertex index of the parent node to print
    :param degree: the degree of sub-children to print
    """
    BRANCH_FORK = "├─ "
    BRANCH_END = "└─ "
    BRANCH_SELF = "● "
    TREE_TRUNK = "│  "
    TREE_EPMTY = "   "

    def print_recursive(vtx: int, deg=1, indent="", branch=""):
        out_degree = graph.vertex(vtx).out_degree()
        print("%s%svtx[%s]" % (indent, branch, vtx),
              "in:", graph.vertex(vtx).in_degree(),
              "out:", out_degree,
              "val:", graph.vp.vertex_name[vtx])

        if branch == BRANCH_FORK:
            indent += TREE_TRUNK
        elif branch == BRANCH_END:
            indent += TREE_EPMTY

        if out_degree and deg:
            for child in graph.get_out_neighbours(vtx)[:-1]:
                if child == vtx:
                    if not branch:
                        branch += BRANCH_FORK
                    print("%s%svtx[%s]" % (indent, branch[:-2] + BRANCH_SELF, child),
                          "in:", graph.vertex(child).in_degree(),
                          "out:", out_degree,
                          "val:", graph.vp.vertex_name[child])
                else:
                    print_recursive(child, deg - 1, indent, BRANCH_FORK)

            child = int(graph.get_out_neighbours(vtx)[-1:])
            if child == vtx:
                if not branch:
                    branch += BRANCH_END
                print("%s%svtx[%s]" % (indent, BRANCH_END[:-2] + BRANCH_SELF, child),
                      "in:", graph.vertex(child).in_degree(),
                      "out:", out_degree,
                      "val:", graph.vp.vertex_name[child])
            else:
                print_recursive(child, deg - 1, indent, BRANCH_END)

    print_recursive(vertex, degree)


def search_vertices(graph: Graph, search_str: str) -> set:
    """
    Searches for nodes which contain the given search string (case sensitive).

    :param graph: the graph containing the nodes
    :param search_str: the string to search for in the node name
    :return: a set of the found vertices or a empty set
    """
    vtx_list = []
    for vtx in graph.vertices():
        vtx_value = graph.vp.vertex_name[vtx]
        if vtx_value.find(search_str) != -1:
            vtx_list.append(vtx)
    return vtx_list


def find_hotspots_out(graph: Graph, top_length=0) -> list:
    """
    Finds the top nodes with most outgoing connections to other nodes ("hotspots").

    :param graph: the graph containing the given nodes
    :param top_length: return the top N results or the top log2(graph_size)+1 if no parameter was given
    :return: a list of nodes with the top most connections
    """
    if top_length <= 0:
        top_length = int(math.log2(len(graph.get_vertices()))) + 1  # use log2 to hold the result list small

    vtx_list = list(graph.vertices())
    vtx_list.sort(key=lambda vertex: vertex.out_degree(), reverse=True)
    del vtx_list[top_length:]

    return vtx_list


def find_hotspots_in(graph: Graph, top_length=0) -> list:
    """
    Finds the top nodes with most intgoing connections to other nodes ("hotspots").

    :param graph: the graph containing the given nodes
    :param top_length: return the top N results or the top log2(graph_size)+1 if no parameter was given
    :return: a list of nodes with the top most connections
    """
    if top_length <= 0:
        top_length = int(math.log2(len(graph.get_vertices()))) + 1  # use log2 to hold the result list small

    vtx_list = list(graph.vertices())
    vtx_list.sort(key=lambda vertex: vertex.in_degree(), reverse=True)
    del vtx_list[top_length:]

    return vtx_list


def print_cycles(graph: Graph):
    """
    Check if graph is a directed acyclic graph (DAG).
    If this is not the case, all cycles in the graph are printed, together with a small statistic about cycle lengths.

    :param graph: input graph
    """
    if is_DAG(graph):
        print("Graph is a DAG. No cycles found!")
        return
    else:
        print("Graph is not a DAG.")
        cycles = list(all_circuits(graph))
        cycles_by_length = dict()
        for c in cycles:
            if len(c) not in cycles_by_length:
                cycles_by_length[len(c)] = list()
            cycles_by_length[len(c)].append(c)

        print("Cycles:")
        print()
        for i in sorted(cycles_by_length.keys()):
            for c in cycles_by_length[i]:
                print(c, end=": ")
                print(graph.vp.vertex_name[c[0]], end="")
                for v in c[1:]:
                    print(" -> {}".format(graph.vp.vertex_name[v]), end="")
                print()

        print()
        print("Found {} cycles in the graph.".format(len(cycles)))
        print()
        print("Number of cycles by length:")
        print("Length | #")
        print("-------+---")
        for i in sorted(cycles_by_length.keys()):
            print("{:>6} | {:<}".format(i, len(cycles_by_length[i])))


def collect_subgraph_vertices(graph: Graph, root_idx: int) -> set:
    """
    Collects all children and sub-children of an given node and return a set of its indices.
    In case of cyclic dependencies, the internal use of a `set` prevents a endless duplication of the nodes in the
    output.

    :param graph: the input graph
    :param root_idx: the root index of the sub-graph
    :return: a set with all node indices of the sub-graph
    """
    vtx_set = set()

    def traverse_recursive(vtx: int):
        vtx_set.add(vtx)
        out_degree = graph.vertex(vtx).out_degree()
        if out_degree:
            for child in graph.get_out_neighbours(vtx):
                if child not in vtx_set and child != vtx:  # ignore self references and cyclic dependencies
                    traverse_recursive(child)

    traverse_recursive(root_idx)
    return vtx_set


class SelectionMode(Enum):
    ALL = 0
    INDEPENDENT = 1


def detect_subgraphs(graph: Graph, is_verbose=True, selection=SelectionMode.ALL):
    """
    Detects sub-graphs in the given input graph.

    :param graph: the input graph
    :param is_verbose: prints output in human readable form or as raw vertex indices for automated processing/piping
    :param selection: the enum which defines the kind of sub-graphs to be printed
                      `ALL`: all detected sub-graphs which may also contain further sub-graphs
                      `INDEPENDENT`: only sub-graphs without any other sub-graphs in it
    """
    indie_nodes = max_independent_vertex_set(graph)
    sub_roots = []
    for vtx in graph.vertices():
        # check if vertex is a subgraph-root and not a leave-node
        if not indie_nodes[vtx] and graph.vertex(vtx).out_degree() > 0:
            sub_roots.append(int(vtx))

    def find_related_sub() -> list:
        related_subgraphs_list = []
        for v in sub_roots:
            sub_children = collect_subgraph_vertices(graph, v)
            sub_children.remove(v)  # remove root-node

            for sub_vtx in sub_roots:
                if sub_vtx in sub_children:
                    related_subgraphs_list.append(v)
                    break
        return related_subgraphs_list

    if is_verbose:  # human readable output
        if selection == SelectionMode.ALL:
            print("Found %s sub-graphs:" % len(sub_roots))
            for vtx in sub_roots:
                sub = collect_subgraph_vertices(graph, vtx)
                sub.remove(vtx)  # remove root-node
                print("sub[%s]" % vtx, "has", len(sub), "children, val:", graph.vp.vertex_name[vtx])

                for vtx_sub in sub_roots:
                    if vtx_sub in sub:
                        print("\t - includes sub[%s]" % vtx_sub, " val:", graph.vp.vertex_name[vtx_sub])

        elif selection == SelectionMode.INDEPENDENT:
            independent_sub_list = []
            related_sub_list = find_related_sub()
            for vtx in sub_roots:
                if vtx not in related_sub_list:
                    independent_sub_list.append(vtx)
            print("Found %s independent sub-graphs:" % len(independent_sub_list))
            for vtx in independent_sub_list:
                print("sub[%s]" % vtx, "val:", graph.vp.vertex_name[vtx])

    else:  # raw output which could be piped in shell
        if selection == SelectionMode.ALL:
            for vtx in sub_roots:
                print("%s " % vtx, end="")
        elif selection == SelectionMode.INDEPENDENT:
            related_sub_list = find_related_sub()
            for vtx in sub_roots:
                if vtx not in related_sub_list:
                    print("%s " % vtx, end="")


def find_subgraphs(graph: Graph) -> dict:
    """
    Searches in the given graph for sub-graphs. The root of an sub-graph is determined by the
    `max_independent_vertex_set()`-function provided by graph-tools.

    :param graph: the graph to search in for sub-graphs
    :return: a list of the found sub-graphs
    """
    indie_nodes = max_independent_vertex_set(graph)
    reduced_list = filter(lambda v: False if indie_nodes[v] else True, graph.vertices())
    subgraph_dict = {}

    for vtx in reduced_list:
        filter_prop = graph.new_vertex_property("bool")
        sub_set = collect_subgraph_vertices(graph, vtx)

        for child in sub_set:
            filter_prop.a[int(child)] = True

        subgraph = GraphView(graph, vfilt=filter_prop)

        # mark the root node with a different color
        subgraph.vp["root"] = subgraph.new_vertex_property("bool")
        subgraph.vp["root"].a[int(vtx)] = True

        subgraph_dict[int(vtx)] = subgraph

    return subgraph_dict


def export_subgraph(graph: Graph, sub_vtx: int, file_name: str):
    """
    Exports the given sub-graph into the `../out/`-directory as `.svg`-file. Since this call may take a long time to
    compute, it should be used carefully.

    :param graph: the input graph
    :param sub_vtx: the root node of the sub-graph
    :param file_name: the name of the exported *.svg-file
    """
    if not os.path.isdir(DEFAULT_OUTPUT_DIR):
        os.mkdir(DEFAULT_OUTPUT_DIR)

    sub = get_subgraph(graph, sub_vtx)
    pos = radial_tree_layout(graph, graph.vertex(sub_vtx))

    graph_draw(sub,
               pos=pos,
               vertex_fill_color='#8ae234cc',  # rrggbbaa
               vertex_text=sub.vertex_index,
               output=DEFAULT_OUTPUT_DIR + file_name + ".svg")


def get_subgraph(graph: Graph, sub_vtx) -> GraphView:
    """
    Gets the given sub-graph from the source graph and stores the result in a new `GraphView` object. This function
    can be used recursive on it's self.

    :param graph: the input graph
    :param sub_vtx: the root node of the sub-graph
    :return: a new `GraphView` with the children of the given sub-graph
    """
    sub_set = collect_subgraph_vertices(graph, sub_vtx)
    filter_prop = graph.new_vertex_property("bool")
    for vtx in graph.vertices():
        if vtx in sub_set:
            filter_prop.a[int(vtx)] = True

    return GraphView(graph, vfilt=filter_prop)


def list_shared_sub_vertices(graph: Graph, vtx_a: int, vtx_b: int) -> list:
    """
    Creates a list with all common shared vertices between two sub-graphs including the root-vertex. Thereby all
    children of each sub-graph where collected and matched against each other. If there is no match, a empty list is
    returned.

    :param graph: the input graph
    :param vtx_a: the first root-vertex of an sub-graph
    :param vtx_b: the second root-vertex of an sub-graph
    :return: a list with all common shared vertex indices or a empty list
    """
    sub_set_a = collect_subgraph_vertices(graph, vtx_a)
    sub_set_b = collect_subgraph_vertices(graph, vtx_b)
    shared_vertex_list = []

    for vtx in sub_set_a:
        if vtx in sub_set_b:
            shared_vertex_list.append(vtx)

    return shared_vertex_list


def exclude_nodes(graph: Graph, excluding_vertex_list: list) -> GraphView:
    """
    Removes the given nodes (vertices) from the source graph and stores the result in a new `GraphView`-object. If
    a removed node has children, all the children and their sub-children getting removed as well.

    :param graph: the input graph
    :param excluding_vertex_list: a list with all vertices which should be excluded
    :return: a new `GraphView` without the vertices of the given list
    """
    filter_prop = graph.new_vertex_property("bool")
    for vtx in graph.vertices():
        if vtx not in excluding_vertex_list:
            filter_prop.a[int(vtx)] = True

    return GraphView(graph, vfilt=filter_prop)


def exclude_subgraph(graph: Graph, sub_vtx) -> GraphView:
    """
    Removes the given sub-graph from the source graph and stores the result in a new `GraphView` object. This function
    can be used recursive on it's self.

    :param graph: the input graph
    :param sub_vtx: the root node of the sub-graph
    :return: a new `GraphView` without the children of the given sub-graph (the sub-graph root-node is kept)
    """
    sub_set = collect_subgraph_vertices(graph, sub_vtx)
    filter_prop = graph.new_vertex_property("bool")
    filter_prop.a[int(sub_vtx)] = True  # keep the root-vertex of the sub-graph
    for vtx in graph.vertices():
        if vtx not in sub_set:
            filter_prop.a[int(vtx)] = True

    out_graph = GraphView(graph, vfilt=filter_prop)
    return out_graph


def export_graph(graph: Graph, out_file=""):
    """
    Exports the given `Graph` or `GraphView`-object into a *.gt-file.

    :param graph: the `Graph` or `GraphView`-object to export
    :param out_file: the file name or a timestamp on default
    """
    if not out_file:
        out_file = strftime("%Y-%m-%d_%H:%M:%S", gmtime())  # use timestamp as default file name

    if not os.path.isdir(DEFAULT_OUTPUT_DIR):
        os.mkdir(DEFAULT_OUTPUT_DIR)

    graph.save(DEFAULT_OUTPUT_DIR + out_file + ".gt")


def nodes_connected(graph: Graph, nodes: list):
    """
    Check weather the given list of nodes are connected in the graph.
    For this, the shortest paths between all node combinations is collected.
    Afterwards, it is checked if those paths are all connected.
    Returns true/false.

    :param graph: the input graph
    :param nodes: list of node IDs or node names
    :return: true if all nodes connected, false otherwise
    """
    # Convert all node names in the list to vertices:
    node_names = [n for n in nodes if not n.isdigit()]
    node_vertices = [graph.vertex(int(n)) for n in nodes if isinstance(n, int) or n.isdigit()]
    for vtx in graph.vertices():
        if graph.vp.vertex_name[vtx] in node_names:
            node_names.remove(graph.vp.vertex_name[vtx])
            node_vertices.append(vtx)
    if not node_names:
        print("Warning: The following node names could not be found in the graph and will be ignored:", node_names)

    # Filter graph by input nodes and the shortest paths between them:
    vprop_filter = graph.new_vertex_property("bool")
    eprop_filter = graph.new_edge_property("bool")
    for v in node_vertices:
        vprop_filter[v] = True
    for (a, b) in itertools.product(node_vertices, node_vertices):
        v_list, e_list = shortest_path(graph, a, b)
        for v in v_list:
            vprop_filter[v] = True
        for e in e_list:
            eprop_filter[e] = True
    graph_filtered = GraphView(graph, vfilt=vprop_filter, efilt=eprop_filter)

    # Check if the graph only consists of one graph
    return bool(len(list(UnconnectedGraphs(graph_filtered))) == 1)


def group(graph: Graph, group_val: str, vtx_group: list) -> GraphView:
    """
    Merges the given group of nodes together into one head-node. The nodes in the group-list getting removed
    afterwards, so only the new head-node and the edges from/to the nodes outside of the group remain in the graph.

    :param graph: the input graph
    :param group_val: the value/name of the new head-vertex
    :param vtx_group: the list of vertices which get merged into the head-vertex
    :return: a new `GraphView` with the given vertices grouped together
    """
    group_head = graph.add_vertex()  # create new head-vertex for the group
    graph.vp.vertex_name[group_head] = group_val  # assign a value/name to the new head-vertex

    # collect all outgoing connections from the group
    out_set = set()
    for vtx in vtx_group:
        for out_vtx in graph.get_out_neighbours(vtx):
            if out_vtx not in vtx_group:
                out_set.add(out_vtx)

    # collect all incoming connections from the group
    in_set = set()
    for vtx in vtx_group:
        for in_vtx in graph.get_in_neighbours(vtx):
            if in_vtx not in vtx_group:
                in_set.add(in_vtx)

    # let the group-head take over outgoing connections
    for o in out_set:
        graph.add_edge(group_head, o)

    # let the group-head take over the incoming connections
    for i in in_set:
        graph.add_edge(i, group_head)

    # filter out grouped vertices
    filter_prop = graph.new_vertex_property("bool")
    for vtx in graph.vertices():
        if vtx not in vtx_group:
            filter_prop.a[int(vtx)] = True

    return GraphView(graph, vfilt=filter_prop)


def parse_node_values(graph: Graph, vertex_values: list) -> list:
    """
    Matches the given value list with the nodes in the input graph and returns the found indices as list.
    This routine is supposed to be a comfort utility function to take nearly every input and translates it into a
    processable output list, whether the input is a list of strings and/or already synthesized indices. If numbers are
    given in the input list, they get interpreted as vertex indices and therefore get bypassed directly into the
    resulting list. If necessary, Numbers could be escaped as string with a leading dot (e.g. `.5`).

    :param graph: the input graph
    :param vertex_values: list with indices node values to match
    :return: a list with the found node indices or a empty list if no vertex index form the input list was given and no
             string match was found
    """
    node_indices = []
    for val in vertex_values:
        if val.isdigit():
            node_indices.append(val)
        else:
            if val[0] == '.':
                val = val[1:]

            was_found = False
            for vtx in graph.vertices():
                vtx_value = graph.vp.vertex_name[vtx]
                if vtx_value == val:
                    node_indices.append(vtx)
                    was_found = True
                    break

            if not was_found:
                print("Could not find Node '%s'. Omit value." % val)

    return node_indices


def add_parent(graph: Graph, parent_val: str, vtx_group: list) -> GraphView:
    """
    Adds a new node to the graph and assigns it to the given vertices as another parent node.

    :param graph: the input graph
    :param parent_val: the value/name of the new parent node
    :param vtx_group: the vertices which become assigned to the new parent
    :return: a new `GraphView` with the new parent node assigned to the given vertices
    """
    parent_node = graph.add_vertex()  # create new parent-vertex for the group
    graph.vp.vertex_name[parent_node] = parent_val  # assign a value/name to the new parent-vertex

    # assign the node as a parent to the group
    for vtx in vtx_group:
        graph.add_edge(parent_node, vtx)

    return GraphView(graph)


def main(argv):
    """
    Main function which parses the passed arguments.

    :param argv: the argument list passed by the command line
    """
    parser = argparse.ArgumentParser(description="A program to analyse and explore large *.dot files.")
    parser.add_argument('file', type=str, metavar='FILE')
    parser.add_argument('-c', '--children', nargs=1, metavar='NODE_ID|NODE_NAME',
                        help="Print the Node and its (sub-)children.")
    parser.add_argument('-p', '--print', nargs='+', metavar='NODE_IDs|NODE_NAMEs',
                        help="Print some details about the given node(s).")
    parser.add_argument('-s', '--search', type=str, nargs='+', metavar='SEARCH_STR', help="Search for the given node.")
    parser.add_argument('-t', '--top', action='store_true',
                        help="Find the top nodes with the most connections (hotspots).")
    parser.add_argument('--cycles', action='store_true', help="Find and print cycles in graph.")
    parser.add_argument('--nodes-connected', type=str, nargs='+', metavar='NODE_ID',
                        help="Check if a list of nodes (id, name) have a connection in the graph. Connections may be "
                             "indirect, e.g. with other nodes in between. Outputs yes/no.")
    parser.add_argument('-ss', '--subgraphs', action='store_true',
                        help="Searches and outputs all sub-graphs from the main graph.")
    parser.add_argument('-sis', '--independent-subgraphs', action='store_true',
                        help="Searches and lists all independent sub-graphs (sub-graphs without any other sub-graphs "
                             "in it).")
    parser.add_argument('--shared', nargs=2, metavar='NODE_ID|NODE_NAME',
                        help="Lists all common shared vertices of two sub-graphs.")
    parser.add_argument('-en', '--exclude-nodes', nargs='+', metavar='NODE_IDs|NODE_NAMEs',
                        help="Excludes the given nodes (and their children) and exports the remaining graph as"
                             "*.gt-file.")
    parser.add_argument('-es', '--exclude-subgraphs', nargs='+', metavar='SUB_ROOT_NODE_IDs|SUB_ROOT_NODE_NAMEs',
                        help="Excludes the given sub-graphs (without root node) and exports the remaining graph as "
                             "*.gt-file.")
    parser.add_argument('-r', '--raw', action='store_true',
                        help="Enable raw output format for further automated processing or piping. This option is "
                             "supported by '--search', '--children', '--subgraphs', '--independent-subgraphs', "
                             "'--shared'.")
    parser.add_argument('--group', nargs='+', metavar=('GROUP_NODE_NAME', 'NODE_IDs|NODE_NAMEs'),
                        help="Merges the given list of node IDs together into one group-node.")
    parser.add_argument('--export', type=str, nargs=1, metavar='FILE-NAME',
                        help="Option to set a specific file name for a exported *.gt-file. This option works in "
                        "combination with '--exclude-nodes', '--exclude-subgraphs', '--group', '--export-subgraph'.")
    parser.add_argument('--add-parent',  nargs='+', metavar=('PARENT_NODE_NAME', 'NODE_IDs|NODE_NAMEs'),
                        help="Adds a new parent node to the given nodes.")
    parser.add_argument('--export-subgraph', nargs=1, metavar='NODE_ID|NODE_NAME',
                        help="Exports the given sub-graph into a *.svg-file.")

    args = parser.parse_args()

    if not args.file:
        print(HELP_INFO_MSG)
        sys.exit(1)
    else:
        graph = load_graph(args.file)

    if args.children:
        node = parse_node_values(graph, args.children)
        if len(node) != 1:
            print("Error: Could not find required  node.")
            sys.exit(1)
        if args.raw:
            for vtx in collect_subgraph_vertices(graph, node[0]):
                print("%s " % vtx, end="")
        else:
            print_vertex_children(graph, node[0], 3)

    if args.print:
        nodes = parse_node_values(graph, args.print)
        for vtx in nodes:
            print_graph_vertex(graph, vtx)

    if args.search:
        for search_str in args.search:
            vertex_set = search_vertices(graph, search_str)

            if args.raw:
                for vtx in vertex_set:
                    print("%s " % vtx, end="")
            else:
                list_len = len(vertex_set)
                if list_len:
                    print("Found %d results for '%s':" % (list_len, search_str))
                    for vtx in vertex_set:
                        vtx_value = graph.vp.vertex_name[vtx]
                        print("vertex[%s]" % int(vtx), vtx_value)
                else:
                    print("No results found for '%s'." % search_str)

    if args.top:
        i = 1
        vertex_list = find_hotspots_out(graph)
        print("Top out-degree nodes:")
        for vtx in vertex_list:
            print("%d." % i,
                  "vtx[%d]" % vtx,
                  "in:", vtx.in_degree(),
                  "out:", vtx.out_degree(),
                  "val:", graph.vp.vertex_name[vtx])
            i += 1

        i = 1
        vertex_list = find_hotspots_in(graph)
        print("Top in-degree nodes:")
        for vtx in vertex_list:
            print("%d." % i,
                  "vtx[%d]" % vtx,
                  "in:", vtx.in_degree(),
                  "out:", vtx.out_degree(),
                  "val:", graph.vp.vertex_name[vtx])
            i += 1

    if args.cycles:
        print_cycles(graph)

    if args.subgraphs:
        detect_subgraphs(graph, not args.raw, SelectionMode.ALL)

    if args.shared:
        nodes = parse_node_values(graph, args.shared)
        if len(nodes) != 2:
            print("Error: Could not find required node for comparison.")
            sys.exit(1)

        shared_vtx_list = list_shared_sub_vertices(graph, nodes[0], nodes[1])
        if args.raw:
            for vtx in shared_vtx_list:
                print("%s " % vtx, end="")
        else:
            print("Shared vertices:")
            print(shared_vtx_list)

    if args.independent_subgraphs:
        detect_subgraphs(graph, not args.raw, SelectionMode.INDEPENDENT)

    if args.exclude_subgraphs:
        nodes = parse_node_values(graph, args.exclude_subgraphs)
        sub = graph
        for sub_vtx in nodes:
            sub = exclude_subgraph(sub, sub_vtx)

        print("Excluded %d sub-graphs" % len(nodes))
        if args.export:
            export_graph(sub, args.export[0])
        else:
            export_graph(sub)

    if args.exclude_nodes:
        nodes = parse_node_values(graph, args.exclude_nodes)
        out_graph = exclude_nodes(graph, nodes)
        print("Excluded %d nodes" % len(nodes))
        if args.export:
            export_graph(out_graph, args.export[0])
        else:
            export_graph(out_graph)

    if args.nodes_connected:
        if nodes_connected(graph, args.nodes_connected):
            print("yes")
        else:
            print("no")

    if args.group:
        if len(args.group) <= 1:
            print("Too few arguments for '--group'. Expected (str, int|str, ...).")
            print(HELP_INFO_MSG)
            sys.exit(1)

        if args.group[0].isdigit():
            print("Group name as to be a string. "
                  "If you really want a number as group name, put a dot in front of it (e.g. '.5') to escape it.")
            print(HELP_INFO_MSG)
            sys.exit(1)
        else:
            if args.group[0][0] == '.':  # escape number as string
                group_name = args.group[0][1:]
            else:
                group_name = args.group[0]

        vtx_list = parse_node_values(graph, args.group[1:])

        if args.export:
            export_graph(group(graph, group_name, vtx_list), args.export[0])
        else:
            export_graph(group(graph, group_name, vtx_list))

    if args.add_parent:
        if len(args.add_parent) <= 1:
            print("Too few arguments for '--add-parent'. Expected (str, int|str, ...).")
            print(HELP_INFO_MSG)
            sys.exit(1)

        if args.add_parent[0].isdigit():
            print("Parent name has to be a string. "
                  "If you really want a number as parent name, put a dot in front of it (e.g. '.5') to escape it.")
            print(HELP_INFO_MSG)
            sys.exit(1)
        else:
            if args.add_parent[0][0] == '.':  # escape number as string
                parent_name = args.add_parent[0][1:]
            else:
                parent_name = args.add_parent[0]

        vtx_list = parse_node_values(graph, args.add_parent[1:])

        if args.export:
            export_graph(add_parent(graph, parent_name, vtx_list), args.export[0])
        else:
            export_graph(out_graph)

    if args.export_subgraph:
        node = parse_node_values(graph, args.export_subgraph)

        if args.export:
            export_subgraph(graph, node[0], args.export[0])
        else:
            export_subgraph(graph, node[0], "sub" + str(node))


if __name__ == "__main__":
    main(sys.argv[1:])
