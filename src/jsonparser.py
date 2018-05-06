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

JSON_FILE_PATH = "../src/bmw-arch.json"
TMP_FILE_PATH = "./bmw-arch.json" #TODO entfernen
TMP_TEST_PATH = "./test.json" #TODO entfernen
TMP_TEST2_PATH = "./test02.json" #TODO entfernen

def _finditemDict(obj, key):
    if type(obj)==list:
        return _finditemList(obj, key)
    elif type(obj)==dict:
        itemlist = []
        if key in obj: itemlist.append(obj[key])#return obj[key]
        for k, v in obj.items():
            if isinstance(v,dict):
                itemlist.append(_finditemDict(v, key))
            elif isinstance(v,list):
                itemlist.append(_finditemList(v, key))
        return itemlist


def _finditemList(obj, key):
    if type(obj)==dict:
        return _finditemDict(obj, key)
    elif type(obj)==list:
        itemlist = []
        for v in obj:
            item = None
            if type(v)==dict:
                item = _finditemDict(v, key)
            elif v==key:#should never happen (we've got no lists in lists)
                item = v
            if item is not None:
                return item
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







def main(argv):
    #data_file = open(TMP_TEST_PATH, encoding="utf-8")
    data_file = open(TMP_TEST2_PATH, encoding="utf-8")
    #data_file = open(TMP_FILE_PATH, encoding="utf-8")
    dataDict = json.loads(data_file.read())

    lis = findAndGetDirectDescendants(dataDict, "telephony-manager")
    print(lis)









#TODO: domainsuche
#TODO: suche mehrerer gleichnamiger sachen


#DONE: ausgabe von nur den komponenten, wenn man zb Connectivity sucht












if __name__ == "__main__":
    main(sys.argv[1:])
