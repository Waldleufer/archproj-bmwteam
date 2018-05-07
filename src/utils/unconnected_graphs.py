#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Split unconnected parts inside a graph into GraphViews"""

from graph_tool.all import *
import argparse

class _ConnectedVisitor(DFSVisitor):
    """Traverse connected graph starting from one given vertex."""

    def __init__(self, vprop_connected, unvisited):
        self.vprop_connected = vprop_connected
        self.unvisited = unvisited

    def discover_vertex(self, v):
        self.vprop_connected[v] = True
        self.unvisited.remove(v)

class UnconnectedGraphs:
    """Iterate over unconnected graphs in a graph. Returns GraphViews."""
    def __init__(self, graph):
        self.graph = graph
        self.graph_undirected = GraphView(graph, directed=False)
        self.unvisited = list(graph.vertices())

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.unvisited) > 0:
            vprop_connected = self.graph_undirected.new_vertex_property("bool")
            connectedVisitor = _ConnectedVisitor(vprop_connected, self.unvisited)
            dfs_search(self.graph_undirected, self.unvisited[0], connectedVisitor)
            return GraphView(self.graph, vfilt=vprop_connected)
        else:
            raise StopIteration

def main():
    arg_parser = argparse.ArgumentParser(description="Extract the largest graph from an input file (DOT, etc.)")
    arg_parser.add_argument('-i', '--input', type=load_graph, required=True, help="Path of the input file")
    arg_parser.add_argument('-o', '--output', type=str, help="Path of the output file")
    args = arg_parser.parse_args()

    Graph(sorted(list(UnconnectedGraphs(args.input)), key=lambda g: g.num_vertices(), reverse=True)[0], prune=True).save(args.output)

    # for sub_graph in UnconnectedGraphs(args.input):
        # print("Subgraph size: ", sub_graph.num_vertices())
        # if sub_graph.num_vertices() < 10:
            # for v in sub_graph.vertices():
                # print("\t", sub_graph.vp.vertex_name[v])

if __name__ == "__main__":
    main()
