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

"""
This script renders a graphic representation of the data in the `descriptors` and the `matrix` lists. Since there
is no routine for parsing external input, the date must copy/pasted into the corresponding lists before execution.
"""
from graph_tool.all import *
import sys
import os

DEFAULT_OUTPUT_DIR = "../../out/"

# the descriptors of the columns/rows
descriptors = ["a", "b", "c", "d", "e", "f"]

# the matrix data
matrix = [[-1, 25, 29, 32, 43, 14],
          [42, -1, 39, 58, 28, 39],
          [32, 28, -1, 21, 28, 40],
          [21, 21, 28, -1, 21, 39],
          [39, 28, 23, 21, -1, 34],
          [41, 39, 41, 39, 34, -1]]

if len(descriptors) != len(matrix):
    print("Error: description list does not match matrix length!")
    sys.exit(1)

g = Graph()
g.add_vertex(len(descriptors))
v_vertex_name = g.new_vertex_property("string")

# create vertices name
for i in range(len(descriptors)):
    v_vertex_name[g.vertex(i)] = descriptors[i]

e_connections = g.new_edge_property("double")

# create connections
for i in range(len(matrix)):
    for j in range(len(matrix[i])):
        val = matrix[j][i]
        if val > 0:
            tmp_edge = g.add_edge(g.vertex(i), g.vertex(j))
            e_connections[tmp_edge] = val / 2.0  # arbitrary coefficient to scale the thickness of the lines

if not os.path.isdir(DEFAULT_OUTPUT_DIR):
    os.mkdir(DEFAULT_OUTPUT_DIR)

state = minimize_nested_blockmodel_dl(g, deg_corr=True)
draw_hierarchy(state,
               # vertex_fill_color="#AA1133EE",
               vertex_text=v_vertex_name,
               edge_pen_width=e_connections,
               output=DEFAULT_OUTPUT_DIR + "out" + ".svg")
