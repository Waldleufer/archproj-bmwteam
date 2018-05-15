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

import argparse
import sys
import math


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
        print("%s%svertex[%d]" % (indent, branch, vtx),
              "in-degree:", graph.vertex(vtx).in_degree(),
              "out-degree:", out_degree,
              "value:", graph.vp.vertex_name[vtx])

        if branch == BRANCH_FORK:
            indent += TREE_TRUNK
        elif branch == BRANCH_END:
            indent += TREE_EPMTY

        if out_degree and deg:
            for child in graph.get_out_neighbours(vtx)[:-1]:
                if child == vtx:
                    if not branch:
                        branch += BRANCH_FORK
                    print("%s%svertex[%d]" % (indent, branch[:-2] + BRANCH_SELF, child),
                          "in-degree:", graph.vertex(child).in_degree(),
                          "out-degree:", out_degree,
                          "value:", graph.vp.vertex_name[child])
                else:
                    print_recursive(child, deg - 1, indent, BRANCH_FORK)

            child = graph.get_out_neighbours(vtx)[-1:]
            if child == vtx:
                if not branch:
                    branch += BRANCH_END
                print("%s%svertex[%d]" % (indent, BRANCH_END[:-2] + BRANCH_SELF, child),
                      "in-degree:", graph.vertex(child).in_degree(),
                      "out-degree:", out_degree,
                      "value:", graph.vp.vertex_name[child])
            else:
                print_recursive(child, deg - 1, indent, BRANCH_END)

    print_recursive(vertex, degree)


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


def find_hotspots(graph: Graph, top_length=0) -> list:
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


def find_subgraphs(graph: Graph) -> list:
    """
    Searches in the given graph for sub-graphs within the given range. The root of an sub-graph is determined by the
    `max_independent_vertex_set()`-function provided by graph-tools.

    :param graph: the graph to search in for sub-graphs
    :return: a list of the found sub-graphs within the range
    """
    indie_nodes = max_independent_vertex_set(graph)
    reduced_list = filter(lambda v: False if indie_nodes[v] else True, graph.get_vertices())
    subgraph_list = []

    for vtx in reduced_list:
        filter_prop = graph.new_vertex_property("bool")
        filter_prop.a[int(vtx)] = True

        for child in graph.get_out_neighbours(vtx):
            filter_prop.a[int(child)] = True

        subgraph = GraphView(graph, vfilt=filter_prop)

        # mark the root node with a different color
        subgraph.vp["root"] = subgraph.new_vertex_property("bool")
        subgraph.vp["root"].a[int(vtx)] = True

        subgraph_list.append(subgraph)

    return subgraph_list


def export_subgraphs(subgraph_list: list, list_range=range(0, 20)):
    """
    Exports a given list of sub-graphs into a `../out/`-directory as `.svg`-files. Since this call may take a long time
    to compute, it is also possible to export only a part of the given list. This makes splitting the task into various
    chunks possible.

    :param subgraph_list: the list containing the sub-graphs as `GraphView` objects.
    :param list_range: a range to export only a part of the given input list
    """
    counter = list_range.start
    for subgraph in subgraph_list:
        graph_draw(subgraph,
                   vertex_fill_color=subgraph.vp.root,
                   vertex_text=subgraph.vertex_index,
                   output="../out/sub" + str(counter) + ".svg")
        counter += 1
        if counter > list_range.stop:
            break


def main(argv):
    """
    Main function which parses the passed arguments.

    :param argv: the argument list passed by the command line
    """
    parser = argparse.ArgumentParser(description="A program to analyse and explore large *.dot files.")
    parser.add_argument('file', type=str, metavar='FILE')
    parser.add_argument('-c', '--children', type=int, metavar='NODE_ID',
                        help="Print the Node and its (sub-)children.")
    parser.add_argument('-p', '--print', action='store_true', help="Print all nodes and their details.")
    parser.add_argument('-s', '--search', type=str, nargs='+', metavar='SEARCH_STR', help="Search for the given node.")
    parser.add_argument('-t', '--top', action='store_true',
                        help="Find the top nodes with the most connections (hotspots).")
    parser.add_argument('--cycles', action='store_true', help="Find and print cycles in graph.")
    parser.add_argument('--subgraphs', action='store_true',
                        help="Searches and outputs sub-graphs from the main graph.")

    args = parser.parse_args()

    if not args.file:
        print("Try 'graph_analyzer -h' for more information.")
        sys.exit(1)
    else:
        graph = load_graph(args.file)

    if args.children:
        print_vertex_children(graph, args.children, 3)

    if args.print:
        print_graph_vertices(graph)

    if args.search:
        for search_str in args.search:
            vertex_list = search_vertices(graph, search_str)
            list_len = len(vertex_list)
            if list_len:
                print("Found %d results for '%s':" % (list_len, search_str))
                for vtx in vertex_list:
                    vtx_value = graph.vp.vertex_name[vtx]
                    print("vertex[%s]" % int(vtx), vtx_value)
            else:
                print("No results found for '%s'." % search_str)

    if args.top:
        vertex_list = find_hotspots(graph)
        for vtx in vertex_list:
            print("vertex[%d]" % vtx,
                  "in-degree:", vtx.in_degree(),
                  "out-degree:", vtx.out_degree(),
                  "value:", graph.vp.vertex_name[vtx])

    if args.cycles:
        print_cycles(graph)

    if args.subgraphs:
        sub_list = find_subgraphs(graph)
        export_subgraphs(sub_list, range(0, 10))  # only export the first 10 subgraphs for testing


if __name__ == "__main__":
    main(sys.argv[1:])
