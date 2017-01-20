#!/bin/bash

# Usage:
# bash pubmed.sh [document_id]
#
# Some error messages will be outputted, but they do not affect the result
# and can't quiet them.
#
# Output is in JSON. Parameters:
# -> doc_id
# -> doc_source
# -> title
# -> abstract (if it exists)
# -> error message (if necessary)
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
