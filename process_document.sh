#!/bin/bash
#set -x
declare docid=$1
declare source=$2
SAVEIFS=$IFS; IFS=$(echo -en "");
if [ $source = "PUBMED" ]; then
    declare title=$(./external_services/pubmed.sh $docid 2>/dev/null| jq '.title')
    declare abstract=$(./external_services/pubmed.sh $docid 2>/dev/null| jq '.abstract')
    declare titleresults=$(./get_entities.sh $docid "T" "$title" "ChEBI")
    declare abstractresults=$(./get_entities.sh $docid "A" $abstract "ChEBI")
    echo $titleresults $abstractresults
fi

