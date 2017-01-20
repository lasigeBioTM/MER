#!/bin/bash

# Usage:
# bash pubmed.sh [document_id1] [document_id2] [document_id3] (...)
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
#     "error_message": "error_message1" (if necessary)
#   },
#   "id2": {
#     "doc_id": "id2",
#     "doc_source": "document_provider2",
#     "title": "title2",
#     "abstract": "abstract2" (if available)
#     "error_message": "error_message2" (if necessary)
#   },
#   "id3": {
#     "doc_id": "id3",
#     "doc_source": "document_provider3",
#     "title": "title3",
#     "abstract": "abstract3" (if available)
#     "error_message": "error_message3" (if necessary)
#   }
# }
#
# Possible error messages:
# -> 'Non-valid id' - ID does not contain any digit between 1 and 9
# -> 'Non-existent id' - ID does not exist

declare non_valid_id_message='Non-valid id'
declare non_existent_id_message='Non-existent id'

declare doc_source='pubmed'

declare output='{}'

for document_id in "$@"; do

  # If document ID is valid
  if grep -q "[1-9]" <<< $document_id; then
      declare xml_response
      declare title
      declare abstract

      xml_response=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=$doc_source&retmode=xml&id=$document_id")
      title=$(xmlstarlet sel -t -v //ArticleTitle <<< $xml_response)
      abstract=$(xmlstarlet sel -t -v //AbstractText <<< $xml_response)
  fi

  # If document ID is not valid
  if ! grep -q "[1-9]" <<< $document_id; then
      output_section=$(jq -n --arg document_id "$document_id" \
                       --arg doc_source "$doc_source" \
                       --arg non_valid_id_message "$non_valid_id_message" \
                       '{($document_id): {"doc_id": $document_id, "source": $doc_source, "error_message": $non_valid_id_message}}')
  # If there is not title, then the ID is non-existent
  elif [[ -z $title ]]; then
      output_section=$(jq -n --arg document_id "$document_id" \
                       --arg doc_source "$doc_source" \
                       --arg non_existent_id_message "$non_existent_id_message" \
                       '{($document_id): {"doc_id": $document_id, "source": $doc_source, "error_message": $non_existent_id_message}}')
  # If there is no abstract
  elif [[ -z $abstract ]]; then
      output_section=$(jq -n --arg document_id "$document_id" \
                      --arg doc_source "$doc_source" \
                      --arg title "$title" \
                      '{($document_id): {"doc_id": $document_id, "source": $doc_source, "title": $title}}')
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
