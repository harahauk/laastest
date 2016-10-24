#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
import datetime
import ConfigParser
# Nedds to be installed
import requests
from elasticsearch import Elasticsearch

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
            #print(" DEBUG: exception on %s!" % option)
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

def set_token_validity(config, seconds):
        now = datetime.datetime.now()
        valid_seconds = time.mktime(now.timetuple()) + int(seconds)
        valid_time = datetime.datetime.fromtimestamp(valid_seconds)
        Config.set('LaasTestCfg', 'oauth_bearer_token_valid',
                valid_time.strftime('%Y-%m-%d %H:%M:%S'))

def is_token_valid(config):
    valid_till = datetime.datetime.strptime(ConfigSectionMap("LaasTestCfg")['oauth_bearer_token_valid'],
            '%Y-%m-%d %H:%M:%S')
    now = datetime.datetime.now()
    if now > valid_till:
        return False
    print "Debug: Token is still valid"
    return True

def auth():
    # sørger for at credentials er satt og gyldige
    save_secret = False
    if (ConfigSectionMap("LaasTestCfg")['oauth_bearer_token'] and
        is_token_valid(Config)):
            # Nothing to do, we have what we need
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
        if not save_secret:
            Config.set('LaasTestCfg', 'oauth_client_secret', "")
        Config.set('LaasTestCfg', 'oauth_bearer_token', token[0])
        set_token_validity(Config, token[1])
        save_config(Config)
        # print "Fikk bearer token " + token

def get_elastic_instance():
    headers = {"Authorization":"Bearer " +
            ConfigSectionMap("LaasTestCfg")['oauth_bearer_token'],
            'User-Agent': 'API Browser'}
    baseurl = ConfigSectionMap("LaasTestCfg")['api_portal']

    es = Elasticsearch([baseurl])
    es.transport.connection_pool.connection.headers.update(headers)
    return es

def search_by_timestamp(index, ip, dateobj):
    """ Search for the document closest to a upper timestamp
    @param index - The laas index
    ip - A string containing IP
    dateobj - a datetime.datetime object with desired timestamp
    """
    to_milliseconds = (float(dateobj.strftime("%s")) * 1000)
    # Grace second
    to_milliseconds = to_milliseconds + 1000

    yesterday = to_milliseconds - 1000*60*60*24
    index_stem = index + "-"
    index_first = (index_stem + str(dateobj.year) + "." +
            str(dateobj.month) + "." +
            str(dateobj.day))
    yesterday_obj = datetime.datetime.fromtimestamp(yesterday / 1e3)
    index_second = (index_stem + str(yesterday_obj.year) + "." +
            str(yesterday_obj.month) + "." +
            str(yesterday_obj.day))
    full_index = index_first + "," + index_second

    body = {
            "sort": [
                { "@timestamp": { "order": "desc" } }
                ],
            'query': {
                "match": {
                    'message': ".*" + ip + ".*"
                    }
            },
            "filter": {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "@timestamp": {
                                    "from": yesterday,
                                    #"to": 1477001273121
                                    "to": to_milliseconds

                                }
                            }
                        }
                            ]
                        }
                    }
        }
    try:
        es = get_elastic_instance()
        res = es.search(index=full_index,
                #terminate_after=100,
                body=body)#,
                #sort={ "_timestamp": "desc" })
                #sort={ "_score": "desc" })
        #print res
        debuglist = []
        for item in res['hits']['hits']:
            debuglist.append(item['_source']['asa_user'] + " " +
                item['_source']['syslog_timestamp'])
        user =  res['hits']['hits'][0]['_source']['asa_user']
        #print debuglist
        return (user, debuglist)

    except Exception, e:
        print e
        return ("Something went wrong", str(e))


def main():
    auth()
    timestamp = raw_input("Gi ett timestamp (2016-10-20 20:59:40): ")
    dateobj = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    ip = raw_input("Gi en IP (129.241.220.133): ")
    user = search_by_timestamp("logs-ntnu-log-vpn", ip, dateobj)
    print "Result: " + user[0]
    print "Loglines: " + str(user[1])

if __name__ == "__main__":
    main()

