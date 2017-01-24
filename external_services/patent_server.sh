#!/bin/bash
# Usage:
# bash patent_server.sh [document_id1] [document_id2] [document_id3] (...)
#
# Some error messages will be outputted, but they do not affect the result
# and can't quiet them.
#
# Output is in JSON and it is something like this:
#
# {
#   "id1": {
#     "doc_id": "id1",
#     "doc_source": "document_provider1",
#     "title": "title1",
#     "abstract": "abstract1" (if available)
#   },
#   "id2": {
#     "doc_id": "id2",
#     "doc_source": "document_provider2",
#     "title": "title2",
#     "abstract": "abstract2" (if available)
#   },
#   "id3": {
#     "doc_id": "id3",
#     "doc_source": "document_provider3",
#     "title": "title3",
#     "abstract": "abstract3" (if available)
#   }
# }
#


declare doc_source="Patent server"

declare output='{}'

#for document_id in "$@"; do

    declare json_response
    declare title
    declare abstract
    declare json_data=$(echo -e "$@"| printf %s "$(cat)" | jq -R -s -c 'split(" ")')
    json_data=$(echo '{"patents":'$json_data'}')
    json_response=$(curl -X POST --header "Content-Type:application/json" -d $json_data  -s http://193.147.85.10:8087/patentserver/json)
    echo $json_response
    
    #title=$(jq '.title' <<< $json_response)
    #abstract=$(jq '.abstractText' <<< $json_response)

    # Removes double quotes
    #title=${title:1:-1}

    # If abstract is available
    #if [[ ! $abstract = 'null' ]]; then
    #    abstract=${abstract:1:-1}

    #    output_section=$(jq -n --arg document_id "$document_id" \
    #                    --arg doc_source "$doc_source" \
    #                    --arg title "$title" \
    #                    --arg abstract "$abstract" \
    #                    '{($document_id): {"doc_id": $document_id, "source": $doc_source, "title": $title, "abstract": $abstract}}')
    #else
    #    output_section=$(jq -n --arg document_id "$document_id" \
    #                     --arg doc_source "$doc_source" \
    #                     --arg title "$title" \
    #                     '{($document_id): {"doc_id": $document_id, "source": $doc_source, "title": $title}}')
    #fi

    #output=$(echo $output "$output_section" | jq -s '.[0] * .[1]')

#done

#echo "$output"
