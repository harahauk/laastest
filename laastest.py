#!/usr/env python
# -*- coding: utf-8 -*-
import ConfigParser
import os
import urllib2
import json
import requests

# Dynamisk konfigfil for mellomlagring av variabler
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

def get_bearer_token(app_id, app_secret):
    print "App ID: " + app_id
    print "App secret: " + app_secret
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    payload = { u'grant_type': u'client_credentials'}
    result = requests.post(ConfigSectionMap("LaasTestCfg")['auth_portal'],
            headers=headers,
            data = payload,
            auth=(app_id, app_secret))
    try:
        token = json.loads(result.text)['access_token']
        return token
    except:
        print "Noe gikk galt:"
        print result.text
        return None

def auth():
    # sørger for at credentials er satt og gyldige
    if ConfigSectionMap("LaasTestCfg")['oauth_bearer_token']:
            #TODO check if expired
            return
    else:
        if not ConfigSectionMap("LaasTestCfg")['oauth_client_id']:
            Config.set('LaasTestCfg', 'oauth_client_id',
                    raw_input("Hva er din klient ID? (lagres til neste gang): "))
            cfgfile = open('config.cfg', 'w')
            Config.write(cfgfile)
            cfgfile.close()
        if not ConfigSectionMap("LaasTestCfg")['oauth_client_secret']:
            Config.set('LaasTestCfg', 'oauth_client_secret',
                    raw_input("Hva er din klient secret? (lagres ikke): "))
            if (raw_input("Vil du lagre secret i klartekst til neste gang? Skriv 'ja': ") == "ja"):
                cfgfile = open('config.cfg', 'w')
                Config.write(cfgfile)
                cfgfile.close()
        token = get_bearer_token(ConfigSectionMap("LaasTestCfg")['oauth_client_id'],
                    ConfigSectionMap("LaasTestCfg")['oauth_client_secret'])
        Config.set('LaasTestCfg', 'oauth_bearer_token', token)
        print "Fikk bearer token " + token

auth()

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

