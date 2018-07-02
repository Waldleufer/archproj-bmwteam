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


"""Show the dependencies inside components, context groups, abstraction layers"""

from graph_tool.all import *
import argparse
import jsonparser
import parent_handler
import graph_analyzer
from utils.unconnected_graphs import UnconnectedGraphs
import graphviz
import os
import itertools

DEFAULT_OUTPUT_DIR = "../out/dependency_graphs/"

NAME_CONVERTER = dict()  # Converts component search names to original names

CLUSTER_COLOR = "grey91"
OUTPUT_FORMAT = "png"

def group_node(graph: Graph, group_val: str, vtx_group: list) -> Vertex:
    """
    Merges the given group of nodes together into one head-node.

    :param graph: the input graph
    :param group_val: the value/name of the new head-vertex
    :param vtx_group: the list of vertices which get merged into the head-vertex
    :return: the new group node
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

    return group_head


def get_vertex_by_name(graph: Graph, name: str):
    """Returns found vertex, or None"""
    for vtx in graph.vertices():
        if name == graph.vp.vertex_name[vtx]:
            return vtx
    return None

def export_dot(graph: Graph, file_name:str ):
    if not os.path.isdir(DEFAULT_OUTPUT_DIR):
        os.mkdir(DEFAULT_OUTPUT_DIR)
    with open(file_name, "w") as f:
        f.write("digraph {\n")
        for (a,b) in graph.edges():
            f.write("\"{}\" -> \"{}\"\n".format(graph.vp.vertex_name[a], graph.vp.vertex_name[b]))
        f.write("}\n")

def connections_view(graph: Graph, vtx_list) -> GraphView:
    vprop_filter = graph.new_vertex_property("bool", val=False)
    eprop_filter = graph.new_edge_property("bool", val=False)
    for v in vtx_list:
        vprop_filter[v] = True
    for a in vtx_list:
        # We precompute all shortest distances to increase preformance
        pred_map = shortest_distance(graph, source=a, target=vtx_list, pred_map=True)[1]
        for b in vtx_list:
            v_list, e_list = shortest_path(graph, graph.vertex(a), graph.vertex(b), pred_map=pred_map)
            for v in v_list:
                vprop_filter[v] = True
            for e in e_list:
                eprop_filter[e] = True
    return GraphView(graph, vfilt=vprop_filter, efilt=eprop_filter)

def init_name_converter(bmw_arch_json: str, task_dependencies_bmw_arch_json: str):
    """Initialize the global dict variable NAME_CONVERTER for converting search names back to original names"""
     # TODO: This should ideally be replaced with a more sophisticated
     # json-file and json parser module
    bmw_arch_json_dict = jsonparser.all_components(bmw_arch_json)
    task_dependencies_bmw_arch_json_dict = jsonparser.all_components(task_dependencies_bmw_arch_json)
    assert(len(bmw_arch_json_dict) == len(task_dependencies_bmw_arch_json_dict))
    for i in range(len(bmw_arch_json_dict)):
        NAME_CONVERTER[task_dependencies_bmw_arch_json_dict[i]] = bmw_arch_json_dict[i]

def sanitize_file_name(name: str):
    """Replaces unwanted characters in file name, e.g., a '/' in the name would result in an unwated new directory
    :returns: sanitized name
    """
    return name.translate({ord('/'): "_", ord(' '): "_", ord('&'): "_"})

def generate_inner_layer_graph(graph: Graph, layer_nodes: list, component_group_dict: dict, directory: str):
    # Generate Graphs for inner structure of layer
    if not os.path.isdir(DEFAULT_OUTPUT_DIR):
        os.mkdir(DEFAULT_OUTPUT_DIR)
    if not os.path.isdir(DEFAULT_OUTPUT_DIR + directory):
        os.mkdir(DEFAULT_OUTPUT_DIR + directory)
    for layer_node in layer_nodes:
        layer_name = graph.vp.vertex_name[layer_node]
        # if layer_name == "telematics":  # TODO: Fix Json file, the remove this
            # continue
        component_groups = [component_group_dict[component_node] for component_node in graph.get_out_neighbors(layer_node)]
        view = connections_view(graph, component_groups)
        export = graphviz.Digraph(name=layer_name,
                directory="{}{}".format(DEFAULT_OUTPUT_DIR, directory),
                filename=sanitize_file_name(layer_name)+".dot",
                engine="dot",
                node_attr={"shape": "box"},
                format=OUTPUT_FORMAT)
        with export.subgraph(name='cluster0') as sub:
            sub.attr(label=layer_name, style="filled", color=CLUSTER_COLOR)
            for vtx in component_groups:
                sub.node(graph.vp.vertex_name[vtx].replace("COMPONENT_GROUP_",""))
        for (a,b) in view.edges():
            export.edge(view.vp.vertex_name[a].replace("COMPONENT_GROUP_",""), view.vp.vertex_name[b].replace("COMPONENT_GROUP_",""))
        export.render()

def generate_outer_layer_graph(graph: Graph, layer_nodes: list, component_group_dict: dict, directory: str):
    """Generates dependency graphs between pairs of two layers."""
    if not os.path.isdir(DEFAULT_OUTPUT_DIR):
        os.mkdir(DEFAULT_OUTPUT_DIR)
    if not os.path.isdir(DEFAULT_OUTPUT_DIR + directory):
        os.mkdir(DEFAULT_OUTPUT_DIR + directory)

    for (layer_node_a, layer_node_b) in itertools.combinations(layer_nodes, 2):
        all_component_groups = list()
        layer_name_a = graph.vp.vertex_name[layer_node_a]
        layer_name_b = graph.vp.vertex_name[layer_node_b]
        # if layer_name_a == "telematics" or layer_name_b == "telematics":  # TODO: Fix Json file, then remove this
            # continue
        export = graphviz.Digraph(name=layer_name_a+"_+_"+layer_name_b,
                directory="{}{}".format(DEFAULT_OUTPUT_DIR, directory),
                filename="{}_-_{}.dot".format(sanitize_file_name(layer_name_a), sanitize_file_name(layer_name_b)),
                engine="dot",
                node_attr={"shape": "box"},
                format=OUTPUT_FORMAT)
        component_groups_a = [component_group_dict[component_node] for component_node in graph.get_out_neighbors(layer_node_a)]
        component_groups_b = [component_group_dict[component_node] for component_node in graph.get_out_neighbors(layer_node_b)]
        with export.subgraph(name='cluster_'+str(layer_node_a)) as sub:
            sub.attr(label=layer_name_a, style="filled", color=CLUSTER_COLOR)
            for vtx in component_groups_a:
                sub.node(graph.vp.vertex_name[vtx].replace("COMPONENT_GROUP_",""))
                all_component_groups.append(vtx)
        with export.subgraph(name='cluster_'+str(layer_node_b)) as sub:
            sub.attr(label=layer_name_b, style="filled", color=CLUSTER_COLOR)
            for vtx in component_groups_b:
                sub.node(graph.vp.vertex_name[vtx].replace("COMPONENT_GROUP_",""))
                all_component_groups.append(vtx)
        view = connections_view(graph, all_component_groups)
        for (a,b) in view.edges():
            export.edge(view.vp.vertex_name[a].replace("COMPONENT_GROUP_",""), view.vp.vertex_name[b].replace("COMPONENT_GROUP_",""))
        export.render()


def main():
    arg_parser = argparse.ArgumentParser(description="Show the dependencies inside components, context groups, abstraction layers, and domains. Output graphs are generated in '../out/'.")
    arg_parser.add_argument('-g', '--graph', type=str, required=True, help="Path to file created by `./parent_handler.py [...] task-depends.dot -c` (../out/parent_handler_output.gt).")
    arg_parser.add_argument('-jo', '--json_original_file', type=str, required=True, help="Path to 'bmw-arch.json' file.")
    arg_parser.add_argument('-js', '--json_search_file', type=str, required=True, help="Path to 'task dependencies bmw-arch.json' file.")
    # arg_parser.add_argument('-c', '--components', action="store_true", help="For each component, do a namespace search and show the dependencies between the found nodes.")
    # arg_parser.add_argument('-o', '--output', type=str, help="Path of the output file")
    args = arg_parser.parse_args()

    print(args.json_original_file, args.json_search_file)
    init_name_converter(args.json_original_file, args.json_search_file)

    # create_parents(args.graph, args.json_file)
    graph = load_graph(args.graph)

    # Extract nodes crated by parent_handler
    context_group_parent_node = get_vertex_by_name(graph, "CONTEXT_GROUPS")

    # Change search names back to original names
    for context_group_node in graph.get_out_neighbors(context_group_parent_node):
        for component_node in graph.get_out_neighbors(context_group_node):
            try:
                graph.vp.vertex_name[component_node] = NAME_CONVERTER[graph.vp.vertex_name[component_node]]
            except:
                print("Warning: search for '{}' could not be converted to original name".format(graph.vp.vertex_name[component_node]))

    if not os.path.isdir(DEFAULT_OUTPUT_DIR):
        os.mkdir(DEFAULT_OUTPUT_DIR)
    if not os.path.isdir(DEFAULT_OUTPUT_DIR + "components"):
        os.mkdir(DEFAULT_OUTPUT_DIR + "components")
    component_vertices_dict = dict()
    # Generate graphs for inner structure of Components and collect vertices to
    # be collected in component_vertices_dict

    print("Listing number of unconnected Graphs in Components, where number > 1, i.e. a coherence violation.")
    print("Unconnected | Component name")
    print("------------+-------------------")
    for context_group_node in graph.get_out_neighbors(context_group_parent_node):
        for component_node in graph.get_out_neighbors(context_group_node):
            component_name = graph.vp.vertex_name[component_node]
            component_vertices = graph.get_out_neighbors(component_node)
            view = connections_view(graph, component_vertices)

            num_graphs = len(list(UnconnectedGraphs(view)))
            if num_graphs > 1:
                print("{:>11} | {:<}".format(num_graphs, component_name))

            component_vertices_dict[component_node] = component_vertices
            export = graphviz.Digraph(name=component_name,
                    directory="{}{}".format(DEFAULT_OUTPUT_DIR, "components"),
                    filename=sanitize_file_name(component_name)+".dot",
                    engine="dot",
                    node_attr={"shape": "box"},
                    format=OUTPUT_FORMAT)
            with export.subgraph(name='cluster0') as sub:
                sub.attr(label=component_name, style="filled", color=CLUSTER_COLOR)
                for vtx in component_vertices:
                    sub.node(graph.vp.vertex_name[vtx])
            for (a,b) in view.edges():
                export.edge(view.vp.vertex_name[a], view.vp.vertex_name[b])
            export.render()

    graph_components_grouped = graph

    # Group all Component vertices together
    component_group_dict = dict()
    for component_node in component_vertices_dict:
        component_group_dict[component_node] = group_node(graph, "COMPONENT_GROUP_" + graph.vp.vertex_name[component_node], component_vertices_dict[component_node])

    # Filter out connections and nodes of grouped vertices:
    vprop_filter = graph.new_vertex_property("bool", val=True)
    eprop_filter = graph.new_edge_property("bool", val=True)
    for component_node in component_vertices_dict:
        for vtx in component_vertices_dict[component_node]:
            for e in graph.get_in_edges(vtx):
                eprop_filter[e] = False
            for e in graph.get_out_edges(vtx):
                eprop_filter[e] = False
            vprop_filter[vtx] = False
    graph_filtered = GraphView(graph, vfilt=vprop_filter, efilt=eprop_filter)

    parent_node = get_vertex_by_name(graph_components_grouped, "CONTEXT_GROUPS")
    nodes = list(graph_filtered.get_out_neighbors(parent_node))
    generate_inner_layer_graph(graph_filtered, nodes, component_group_dict, "context_groups_inner")
    generate_outer_layer_graph(graph_filtered, nodes, component_group_dict, "context_groups_outer")

    parent_node = get_vertex_by_name(graph_components_grouped, "ABSTRACTION_LAYERS")
    nodes = list(graph_filtered.get_out_neighbors(parent_node))
    generate_inner_layer_graph(graph_filtered, nodes, component_group_dict, "abstraction_layers_inner")
    generate_outer_layer_graph(graph_filtered, nodes, component_group_dict, "abstraction_layers_outer")

    parent_node = get_vertex_by_name(graph_components_grouped, "DOMAINS")
    nodes = list(graph_filtered.get_out_neighbors(parent_node))
    generate_inner_layer_graph(graph_filtered, nodes, component_group_dict, "domains_inner")
    generate_outer_layer_graph(graph_filtered, nodes, component_group_dict, "domains_outer")


if __name__ == "__main__":
    main()
