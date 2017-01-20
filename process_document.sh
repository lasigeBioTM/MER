#!/bin/bash
#set -x
declare docid=$1
declare section=$2
declare text=$3

SAVEIFS=$IFS; IFS=$(echo -en "");

declare results=$(./get_entities.sh $docid $section "$text" "CHEMICAL" 2>/dev/null)
echo $results

