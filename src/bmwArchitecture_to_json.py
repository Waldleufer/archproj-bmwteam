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

import json


def addListWithSameGroups(jsonfile: str, componentList: list, domain: str, contextGroup: str, hardwareGroup: str):
    """
    appends a List of components to the jsonfile that have the same domain, the same contextGroup and the same hardwareGroup
    param jsonfile: name of file where to add the names as string
    param namelist: list with names to add
    param domain: domain that shall be apllied to all items of namelist
    param contextGroup: contextGroup of all items
    param hardwareGroup: hardwareGroup of all items
    """
    with open(jsonfile, "a") as append_file:

        dataList = list()

        for component in componentList:

            comp = {
                component: {
                    "domain": domain,
                    "contextGroup": contextGroup,
                    "hardwareGroup": hardwareGroup
                }
            }
            dataList.append(comp)
        append_file.write(json.dumps(dataList, indent=2))
