#!/bin/bash
# Usage:
# bash patent_server.sh [document_id1] [document_id2] [document_id3] (...)
#
#
# Output is in JSON and it is something like this:
#
# [
#   {
#     "externalId": "id1",
#     "title": "title1",
#     "abstractText": "abstract1"
#   },
#   {
#     "externalId": "id2",
#     "title": "title2",
#     "abstractText": "abstract2"
#   },
#   {
#     "externalId": "id3",
#     "title": "title3",
#     "abstractText": "abstract3"
#   },
# ]
#

declare json_response
declare json_data
json_data=$(echo -e "$@"| printf %s "$(cat)" | jq -R -s -c 'split(" ")')
json_data='{"patents":'$json_data'}'
json_response=$(curl -X POST --header "Content-Type:application/json" -d "$json_data"  -s http://193.147.85.10:8087/patentserver/json)
echo "$json_response"

