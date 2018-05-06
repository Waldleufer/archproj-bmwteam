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

import sys #TODO entfernen?
import json
from pprint import pprint #TODO entfernen

JSON_FILE_PATH = "../tests/jsonparser/bmw-arch.json"


def _finditemDict(obj, key):
    if type(obj)==list:
        return _finditemList(obj, key)
    elif type(obj)==dict:
        itemlist = []
        if key in obj: itemlist = itemlist + obj[key]
            #for i in obj[key]
            #    itemlist.append(obj[key][i])#return obj[key]
        #this should be irrelevant
        for k, v in obj.items():
            if isinstance(v,dict):
                item = _finditemDict(v, key)
                if item is not None: itemlist.append(item)
            elif isinstance(v,list):
                item = _finditemList(v, key)
                if item is not None: itemlist.append(item)
        if len(itemlist) != 0:
            return itemlist
        else:
            return None


def _finditemList(obj, key):
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


#returns the keys children as a list of dictionaries 
#(except the key is too deep in the object, e.g. "domain")
#or an empty list, if nothing is found
def finditem(obj, key):
    item = _finditemDict(obj, key)
    if item is not None:
        #print(key + ":", item)
        return item
    else:
        #print("Nothing found.")
        return []


#lis: list of dictionaries
#prints only the keys of every dictionary
#output: all keys of the dictionaries in a list 
#        or an empty list, if lis is None or a dictionary (meaning there are no more children) 
def getDirectDescendants(lis):
    if type(lis)==dict: return []
    desc = []
    for dic in lis:
        for k in dic:
            desc.append(k)
    return desc


#dic: dictionary in our bmwteam-schema
#key: a key to be searched
#output: a list of all direct children-names of the key or None if nothing is found
#this funktion combines finditem and getDirectDescendants for easier use
def findAndGetDirectDescendants(dic, key):
    itemList = finditem(dic, key)
    desc = getDirectDescendants(itemList)
    return desc



#dic: dictionary in our bmwteam-schema
#output: one dictionary containing every module and its "domain", "contextGroup" and "hardwareGroup"
def breakdownDict(dic):
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
    

#dic: dictionary in our bmwteam-schema
#domain: the domain of which content is requested
#output: a list of modules in the requested domain
def searchByDomain(dic, domain):
    #This is to check whether everything was inputted correctly in our json file    
    #domains = ["apposs","cia","connectivity","distrender","entertainment","hmi",
    #            "navigation","speech","supersec","sysfunc","sysinfra","telematics"]
    modules = breakdownDict(dic)
    #pprint(modules)
    domainlist = []
    for k,v in modules.items():
        #if(v["domain"] not in domains and v["domain"] is not None):
        if(v["domain"] == domain):
            domainlist.append(k)
    return domainlist

#dic: dictionary in our bmwteam-schema
#context: the contextGroup of which content is requested
#output: a list of modules in the requested contextGroup
def searchByContext(dic, context):
    #This is to check whether everything was inputted correctly in our json file
    #contexts = ["Connectivity","Multimedia","Navigation","Speech", "Telematics / OAP","CE integration / A4A","Filesystem","Data","IPC","Runtime environment Framework libraries","Network","Lifecycle / diversity","SysInfra managers","System functions","Security","Log&Trace / debug","Graphic","Audio / Video","Linux infrastructure","Kernel / bootloader","Drivers / firmware"]
    modules = breakdownDict(dic)
    contextlist = []
    for k,v in modules.items():
        #if(v["contextGroup"] not in contexts and v["contextGroup"] is not None):
        if(v["contextGroup"] == context):
            contextlist.append(k)
    return contextlist

#dic: dictionary in our bmwteam-schema
#hardware: the hardwareGroup of which content is requested
#output: a list of modules in the requested hardwareGroup
def searchByHardware(dic, hardware):
    '''
    #This is to check whether everything was inputted correctly in our json file
    hardwares = ["Presentation", "Middleware", "Middleware - OnlineApp platform", "Services", "Presentation - OnlineApps",
"Services - Telematics platform - Infrastructure", "Services - Telematics platform - Iterface-vehicle",
"System Infrastructure - off-the-shelf", "System Infrastructure - off-the-shelf - compression", "System Infrastructure - off-the-shelf - rendering", "System Infrastructure - off-the-shelf - imaging", "System Infrastructure - off-the-shelf - string", "System Infrastructure - off-the-shelf - json", "System Infrastructure - off-the-shelf - xml", "System Infrastructure - off-the-shelf - Audio / AVB stack",
"System Infrastructure - product specific", "System Infrastructure - product specific - RSU", "System Infrastructure - product specific - Personalization", "System Infrastructure - product specific - Diversity",
"BSP", "BSP - HAL / audo", "BSP - HAL / graphic"]
    '''
    modules = breakdownDict(dic)
    hardwarelist = []
    for k,v in modules.items():
        #if(v["hardwareGroup"] not in hardwares and v["hardwareGroup"] is not None):
        if(v["hardwareGroup"] == hardware):
            hardwarelist.append(k)
    return hardwarelist


def main(argv):
    data_file = open(JSON_FILE_PATH, encoding="utf-8")
    dataDict = json.loads(data_file.read())


    '''
    Anwendungswege
    '''
    #lis = findAndGetDirectDescendants(dataDict, "Context Groups")
    #print(lis)

    #domainlist = searchByDomain(dataDict, "navigation")
    #print(domainlist)

    #contextlist = searchByContext(dataDict, "Navigation")
    #print(contextlist)

    #hardwarelist = searchByHardware(dataDict, "Presentation")
    #print(hardwarelist)
















if __name__ == "__main__":
    main(sys.argv[1:])
