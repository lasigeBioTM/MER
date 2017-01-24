#!/bin/bash

# Usage:
# bash pmc.sh [document_id1] [document_id2] [document_id3] (...)
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
#     "title": "title1", (if available)
#     "abstract": "abstract1", (if available)
#     "error_message": "error_message1" (if necessary)
#   },
#   "id2": {
#     "doc_id": "id2",
#     "doc_source": "document_provider2",
#     "title": "title2", (if available)
#     "abstract": "abstract2", (if available)
#     "error_message": "error_message2" (if necessary)
#   },
#   "id3": {
#     "doc_id": "id3",
#     "doc_source": "document_provider3",
#     "title": "title3", (if available)
#     "abstract": "abstract3", (if available)
#     "error_message": "error_message3" (if necessary)
#   }
# }
#
# Possible error messages:
# -> 'Non-existent id' - ID does not exist

declare non_existent_id_message='Non-existent id'

declare doc_source='pmc'

declare output='{}'

for document_id in "$@"; do

    declare xml_response
    declare title
    declare abstract

    xml_response=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=$doc_source&retmode=xml&id=$document_id")
    title=$(xmlstarlet sel -t -v //article-title <<< $xml_response)
    abstract=$(xmlstarlet sel -t -v //abstract/p <<< $xml_response)

    # If there is no abstract
    if [[ -z $abstract ]]; then
       if [[ -z $title ]]; then
          output_section=$(jq -n --arg document_id "$document_id" \
                           --arg doc_source "$doc_source" \
                           --arg non_existent_id_message "$non_existent_id_message" \
                           '{($document_id): {"doc_id": $document_id, "source": $doc_source, "error_message": $non_existent_id_message}}')
        else
          output_section=$(jq -n --arg document_id "$document_id" \
                          --arg doc_source "$doc_source" \
                          --arg title "$title" \
                          '{($document_id): {"doc_id": $document_id, "source": $doc_source, "title": $title}}')
        fi
    else
      output_section=$(jq -n --arg document_id "$document_id" \
                       --arg doc_source "$doc_source" \
                       --arg title "$title" \
                       --arg abstract "$abstract" \
                       '{($document_id): {"doc_id": $document_id, "source": $doc_source, "title": $title, "abstract": $abstract}}')
    fi

    # Merge with output being constructed
    output=$(echo $output "$output_section" | jq -s '.[0] * .[1]')

done

echo "$output"
