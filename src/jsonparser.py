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

import sys #only used for usage examples
import json

JSON_FILE_PATH = "../tests/bmw-arch.json"


def _breakdownDict(dic):
    """
    Breaks down our whole bmw-json schema into a single dictionary.
    param dic: a dictionary in our bmw-json schema.
    return: a single dictionary containing every module and its "domain", "contextGroup" and "hardwareGroup" without any deeper lists or dictionaries.
    """
    modules = {}
    for k1,v1 in dic.items():#dict 1 - k1=contextGroups, v1=List of context group
        for l1 in v1:#list 1 - l1=dict of hw-levels
            for k2,v2 in l1.items():#dict 2 - k2=e.g.connectivity, v2=e.g.list of dict with presentation, services, ...
                for l2 in v2:#list 2
                    for k3,v3 in l2.items():#dict 3
                        for l3 in v3:#list 3
                            for k4,v4 in l3.items():#dict 4
                                modules[k4] = v4
    return modules


def searchByDomain(file_path, domain):
    """
    Searches a dictionary in our bmw-json schema for every module inside the given domain.
    param file_path: the path to the json file to be searched. It should be in our bmw-json schema.
    param domain: the domain of which content is requested.
    return: a list of every module inside the given domain.
    """
    #This list can be used to check whether everything was inputted correctly into our json file. It contains every domain.
    #domains = ["apposs","cia","connectivity","distrender","entertainment","hmi",
    #            "navigation","speech","supersec","sysfunc","sysinfra","telematics"]
    path = file_path
    if path == "": path = JSON_FILE_PATH
    data_file = open(path, encoding="utf-8")
    dic = json.loads(data_file.read())

    modules = _breakdownDict(dic)
    domainlist = []
    for k,v in modules.items():
        #if(v["domain"] not in domains and v["domain"] is not None):
        if(v["domain"] == domain):
            domainlist.append(k)
    return domainlist


def searchByContext(file_path, context):
    """
    Searches a dictionary in our bmw-json schema for every module inside the given contextGroup.
    param file_path: the path to the json file to be searched. It should be in our bmw-json schema.
    param context: the contextGroup of which content is requested.
    return: a list of every module inside the given contextGroup.
    """
    #This list can be used to check whether everything was inputted correctly into our json file. It contains every contextGroup.
    #contexts = ["Connectivity","Multimedia","Navigation","Speech", "Telematics / OAP","CE integration / A4A","Filesystem","Data","IPC","Runtime environment Framework libraries","Network","Lifecycle / diversity","SysInfra managers","System functions","Security","Log&Trace / debug","Graphic","Audio / Video","Linux infrastructure","Kernel / bootloader","Drivers / firmware"]
    path = file_path
    if path == "": path = JSON_FILE_PATH
    data_file = open(path, encoding="utf-8")
    dic = json.loads(data_file.read())

    modules = _breakdownDict(dic)
    contextlist = []
    for k,v in modules.items():
        #if(v["contextGroup"] not in contexts and v["contextGroup"] is not None):
        if(v["contextGroup"] == context):
            contextlist.append(k)
    return contextlist


def searchByHardware(file_path, hardware):
    """
    Searches a dictionary in our bmw-json schema for every module inside the given contextGroup.
    param file_path: the path to the json file to be searched. It should be in our bmw-json schema.
    param hardware: the hardwareGroup of which content is requested.
    return: a list of every module inside the given hardwareGroup.
    """
    #This list can be used to check whether everything was inputted correctly into our json file. It contains every hardwareGroup.
    #hardwares = ["Presentation", "Middleware", "Middleware - OnlineApp platform", "Services", "Presentation - OnlineApps",
    #"Services - Telematics platform - Infrastructure", "Services - Telematics platform - Iterface-vehicle",
    #"System Infrastructure - off-the-shelf", "System Infrastructure - off-the-shelf - compression", "System Infrastructure - off-the-shelf - rendering", "System Infrastructure - off-the-shelf - imaging", "System Infrastructure - off-the-shelf - string", "System Infrastructure - off-the-shelf - json", "System Infrastructure - off-the-shelf - xml", "System Infrastructure - off-the-shelf - Audio / AVB stack",
    #"System Infrastructure - product specific", "System Infrastructure - product specific - RSU", "System Infrastructure - product specific - Personalization", "System Infrastructure - product specific - Diversity",
    #"BSP", "BSP - HAL / audo", "BSP - HAL / graphic"]
    path = file_path
    if path == "": path = JSON_FILE_PATH
    data_file = open(path, encoding="utf-8")
    dic = json.loads(data_file.read())

    modules = _breakdownDict(dic)
    hardwarelist = []
    for k,v in modules.items():
        #if(v["hardwareGroup"] not in hardwares and v["hardwareGroup"] is not None):
        if(v["hardwareGroup"] == hardware):
            hardwarelist.append(k)
    return hardwarelist






'''
usage example
'''

#domainlist = searchByDomain("", "navigation")
#print(domainlist)

#contextlist = searchByContext("", "Navigation")
#print(contextlist)

#hardwarelist = searchByHardware("", "Presentation")
#print(hardwarelist)



