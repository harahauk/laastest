# laastest
Lite prosjekt for å få data ut av laas-api

# Nyttige kommandoer å huske

# Eksempel for å få token
curl -XPOST https://auth.dataporten.no/oauth/token -u
'<Ditt token>' --data 'grant_type=client_credentials'

## Eksempel for å få ut data, queryet finner man i laas ved å inspecte ett gitt søk eller skrive ett eget

url -v -H 'Authorization: Bearer <Ditt token>'
'https://laas.dataporten-api.no/logs-ntnu-apptest-2016.10.13,logs-ntnu-apptest-2016.10.12/_search?pretty'
-d '{ "facets": { "0": { "date_histogram": { "field": "@timestamp", "interval":
"10m" }, "global": true, "facet_filter": { "fquery": { "query": { "filtered": {
    "query": { "query_string": { "query": "*" } }, "filter": { "bool": { "must":
    [ { "range": { "@timestamp": { "from": 1476256858889, "to": 1476343258889 }
    } } ] } } } } } } } }, "size": 0 }'
