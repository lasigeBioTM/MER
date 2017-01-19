#!/bin/bash

# Usage:
# bash patent_server.sh [document_id]
#
# Some error messages will be outputted, but they do not affect the result
# and can't quiet them.
#
# Output is in JSON. Parameters:
# -> doc_id
# -> doc_source
# -> title
# -> abstract

declare document_id=$1
declare doc_source="Patent server"

declare json_response
declare title
declare abstract

json_response=$(curl -s http://193.147.85.10:8087/patentserver/json/"$document_id")
title=$(jq '.title' <<< $json_response)
abstract=$(jq '.abstractText' <<< $json_response)

# Removes double quotes
title=${title:1:-1}
abstract=${abstract:1:-1}

output=$(jq -n --arg document_id "$document_id" \
            --arg doc_source "$doc_source" \
            --arg title "$title" \
            --arg abstract "$abstract" \
            '{"doc_id": $document_id, "source": $doc_source, "title": $title, "abstract": $abstract}')

echo "$output"
