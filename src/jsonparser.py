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

JSON_FILE_PATH = "../tests/jsonparser/bmw-arch.json"

def _finditemDict(obj, key):
    """
    Returns a list of every found key in the given dictionary.
    If there are lists or dictionaries inside, those are also searched with a recursive call or _finditemList().
    param obj: the dictionary to be searched. This should be a dictionary like in our bmw-json schema.
    param key: the key to be searched in obj.
    return: a list of dictionaries containig all descendants of every found key-entry or None if nothing is found.
    """
    if type(obj)==list:
        return _finditemList(obj, key)
    elif type(obj)==dict:
        itemlist = []
        if key in obj and type(obj[key])!=str and obj[key]!=None:
            itemlist = itemlist + obj[key]
        for k, v in obj.items():
            if isinstance(v,dict):
                item = _finditemDict(v, key)
                if item is not None: itemlist = itemlist + item
            elif isinstance(v,list):
                item = _finditemList(v, key)
                if item is not None: itemlist = itemlist + item
        if len(itemlist) != 0:
            return itemlist
        else:
            return None


def _finditemList(obj, key):
    """
    Returns a list of every found key in the given list.
    If there are lists or dictionaries inside, those are also searched with a recursive call or _finditemDict().
    param obj: the list to be searched. This should be a list like in our bmw-json schema.
    param key: the key to be searched in obj.
    return: a list of dictionaries containig all descendants of every found key-entry in deeper dictionaries or None if nothing is found.
    """
    if type(obj)==dict:
        return _finditemDict(obj, key)
    elif type(obj)==list:
        itemlist = []
        for v in obj:
            if type(v)==dict:
                item = _finditemDict(v, key)
                if item is not None: itemlist = itemlist + item
            elif v==key:#should never happen (we've got no lists in lists)
                itemlist.append(v)
        if len(itemlist) != 0:
            return itemlist
        else:
            return None


def finditem(obj, key):
    """
    Returns the key-entrys children as a list of dictionaries.
    (except the key is too deep in the object and its children arent further dictionaries, e.g. "domain")
    param obj: the dictionary to be searched. This should be in our bmw-json schema.
    param key: the key to be searched in obj.
    return: the key-entrys children as a list of dictionaries or an empty list if there are no deeper dictionaries or nothing is found.
    """
    item = _finditemDict(obj, key)
    if item is not None:
        #print(key + ":", item)
        return item
    else:
        #print("Nothing found.")
        return []


def getDirectDescendants(lis):
    """
    Gets a list of dictionaries and returns only the keys of all dictionaries in a list.
    param lis: a list of dictionaries.
    return: a list of every key from all the dictionaries (doesn't look deeper into each dictionary).
    """
    desc = []
    for dic in lis:
        for k,v in dic.items():
            desc.append(k)
    return desc


def findAndGetDirectDescendants(file_path, key):
    """
    Combines finditem and getDirectDescendants for easier use and takes a filepath instead of an dictionary.
    param file_path: the path to the json file to be searched. It should be in our bmw-json schema.
    param key: the key to be searched in dic.
    return: the names of any direct descendant of every occurrence of the key in dic in a list.
    """
    path = file_path
    if path == "": path = JSON_FILE_PATH
    data_file = open(path, encoding="utf-8")
    dic = json.loads(data_file.read())

    itemList = finditem(dic, key)
    desc = getDirectDescendants(itemList)
    return desc




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

#lis = findAndGetDirectDescendants("", "Context Groups")
#lis = findAndGetDirectDescendants("", "Middleware")
#print(lis)

#domainlist = searchByDomain("", "navigation")
#print(domainlist)

#contextlist = searchByContext("", "Navigation")
#print(contextlist)

#hardwarelist = searchByHardware("", "Presentation")
#print(hardwarelist)



