#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


"""Computes the number of dependent tasks, given a task-depends.dot file."""

from graph_tool.all import *
import argparse

class _MarkDependencySubgraph(DFSVisitor):
    def __init__(self, vprop_dependency_subgraph):
        self.vprop_dependency_subgraph = vprop_dependency_subgraph

    def discover_vertex(self, v):
        self.vprop_dependency_subgraph[v] = 1

class _DependencyCountVisitor(DFSVisitor):
    def __init__(self, graph, vprop_dependency_count):
        self.graph = graph
        self.vprop_dependency_count = vprop_dependency_count

    def discover_vertex(self, v):
        vprop_dependency_subgraph = self.graph.new_vertex_property("bool", 0)
        markDependencySubgraphVisitor = _MarkDependencySubgraph(vprop_dependency_subgraph)
        dfs_search(self.graph, v, markDependencySubgraphVisitor)
        self.vprop_dependency_count[v] = markDependencySubgraphVisitor.vprop_dependency_subgraph.a.sum() - 1


def main():
    arg_parser = argparse.ArgumentParser(description="For each task in a task-depends.dot file compute the number of dependent tasks (default) or tasks that require this task. This includes also indirect rquirements, so the size of the whole subtree is counted.")
    arg_parser.add_argument('file', type=str, metavar='task-depends.dot')
    arg_parser.add_argument('--reverse', '-r', action="store_true",
            help="Reverse dependencies: Instead of counting dependencies, this will count the tree of tasks that require a task. Finds top task that, when changed, imply the biggest impact on other tasks (i.e. they must be rebuild).")
    arg_parser.add_argument('-t', '--top', type=int, metavar='N',
            help="Limit output to the top n nodes with the most dependencies.")

    args = arg_parser.parse_args()

    graph = load_graph(args.file)

    if args.reverse:
        graph.set_reversed(True)

    if not is_DAG(graph):
        print("Fatal error: Graph is not acyclic. No computation can be performed.")
        import sys
        sys.exit(1)

    vprop_dependency_count = graph.new_vertex_property("int", 0)
    dependencyCountVisior = _DependencyCountVisitor(graph, vprop_dependency_count)
    dfs_search(graph, visitor=dependencyCountVisior)


    vertices = list(graph.vertices())
    print("Count | Task Name")
    print("------+-------------------")
    for v in sorted(vertices, key=lambda v: vprop_dependency_count[v], reverse=True):
        if args.top is not None:
            if args.top <= 0:
                break
            else:
                args.top -= 1
        print("{:>5} | {:<}".format(vprop_dependency_count[v], graph.vp.vertex_name[v]))


if __name__ == "__main__":
    main()
