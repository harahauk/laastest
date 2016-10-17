#!/usr/env python
# -*- coding: utf-8 -*-
import ConfigParser
import os
import urllib2
import json
import requests

Config = ConfigParser.ConfigParser()
Config.read('config.cfg')

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

headers = {"Authorization":"Bearer " +
        ConfigSectionMap("LaasTestCfg")['oauth_bearer_token'],
        'User-Agent': 'API Browser'}
#TODO: Auth
#TODO: Hent nytt token om det andre er utgått
#Config.set('LaasTestCfg', 'auth_portal', "ingenting")

baseurl = ConfigSectionMap("LaasTestCfg")['api_portal']

# Eksempel på søk
query_partitions = "logs-ntnu-apptest-2016.10.16,logs-ntnu-apptest-2016.10.15/_search?pretty"
def search(uri):
    query = json.dumps({
        "query": {
            "query_string": {
                "query": "@timestamp:(\"2016-10-15T07:31:01.438Z\")"
            }
        }
    })

    response = requests.get(uri, headers=headers, data=query)
    results = json.loads(response.text)
    return results

print search(baseurl + query_partitions)

