#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
import json
import requests

# Dynamisk konfigfil for mellomlagring av variabler
Config = ConfigParser.ConfigParser()
Config.read('config.cfg')

# Hjelpefunksjon for å hente ut config
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
    # OAUTH
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    payload = { u'grant_type': u'client_credentials'}
    result = requests.post(ConfigSectionMap("LaasTestCfg")['auth_portal'],
            headers=headers,
            data = payload,
            auth=(app_id, app_secret))
    try:
        token = json.loads(result.text)
        return (token['access_token'], token['expires_in'])
    except:
        print "Noe gikk galt med OAUTH, feilmelding følger:"
        print result.text
        return None

def save_config(config):
    cfgfile = open('config.cfg', 'w')
    config.write(cfgfile)
    cfgfile.close()

def auth():
    save_secret = False
    # sørger for at credentials er satt og gyldige
    if ConfigSectionMap("LaasTestCfg")['oauth_bearer_token']:
            #TODO check if expired
            return
    else:
        if not ConfigSectionMap("LaasTestCfg")['oauth_client_id']:
            Config.set('LaasTestCfg', 'oauth_client_id',
                    raw_input("Hva er din klient ID? (lagres til neste gang): "))
            save_config(Config)
        if not ConfigSectionMap("LaasTestCfg")['oauth_client_secret']:
            Config.set('LaasTestCfg', 'oauth_client_secret',
                    raw_input("Hva er din klient secret? (lagres ikke): "))
            if (raw_input("Vil du lagre secret i klartekst til neste gang? Skriv 'ja': ") == "ja"):
                save_secret = True
        token = get_bearer_token(ConfigSectionMap("LaasTestCfg")['oauth_client_id'],
                    ConfigSectionMap("LaasTestCfg")['oauth_client_secret'])
        if not save_config:
            Config.set('LaasTestCfg', 'oauth_client_secret', "")
        Config.set('LaasTestCfg', 'oauth_bearer_token', token[0])
        Config.set('LaasTestCfg', 'oauth_bearer_token_valid', token[1])
        save_config(Config)
        # print "Fikk bearer token " + token

auth()

headers = {"Authorization":"Bearer " +
        ConfigSectionMap("LaasTestCfg")['oauth_bearer_token'],
        'User-Agent': 'API Browser'}
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

