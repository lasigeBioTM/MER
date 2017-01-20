#!/bin/bash
#set -x
declare docid=$1
declare source=$2
SAVEIFS=$IFS; IFS=$(echo -en "");
if [ $source = "PUBMED" ]; then
    declare script=$(echo "pubmed")
elif [ $source = "PATENT SERVER" ]; then
    declare script=$(echo "patent_server")
fi

declare title=$(./external_services/$script.sh $docid 2>/dev/null| jq '.title')
declare abstract=$(./external_services/$script.sh $docid 2>/dev/null| jq '.abstract')
declare titleresults=$(./get_entities.sh $docid "T" "$title" "all_terms" 2>/dev/null)
declare abstractresults=$(./get_entities.sh $docid "A" $abstract "all_terms" 2>/dev/null)
echo $titleresults
echo $abstractresults

