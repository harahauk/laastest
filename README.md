# LaasTest
Lite prosjekt for å få data ut av laas-API

# Requirements
Python 2.7
pip install requests

# Andre ting
På https://docs.dataporten.no/ finner man link til dashboard, oauth_secret og ID
finner man på "Prosjektnavn" -> Ouath detaljer. Om man har en token kan man lime
den inn i cfg-fila, men programmet skal spørre deg om slikt dynamisk snart.

# Nyttige kommandoer å huske før det er innbakt i programmet

Eksempel for å få token
```bash
curl -XPOST https://auth.dataporten.no/oauth/token -u
'<Din client_id>' --data 'grant_type=client_credentials'
``` 

(Stygt) Eksempel for å få ut data, queryet finner man i laas ved å inspecte ett gitt søk eller skrive ett eget
```bash
url -v -H 'Authorization: Bearer <Ditt token>'
'https://laas.dataporten-api.no/logs-ntnu-apptest-2016.10.13,logs-ntnu-apptest-2016.10.12/_search?pretty'
-d '{ "facets": { "0": { "date_histogram": { "field": "@timestamp", "interval":
"10m" }, "global": true, "facet_filter": { "fquery": { "query": { "filtered": {
    "query": { "query_string": { "query": "*" } }, "filter": { "bool": { "must":
    [ { "range": { "@timestamp": { "from": 1476256858889, "to": 1476343258889 }
    } } ] } } } } } } } }, "size": 0 }'
```
