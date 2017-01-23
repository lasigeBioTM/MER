#!/bin/bash

#set -x #debug

declare POST_DATA=$1

declare key=$(echo "e2b88b40674b13e92fc6e41aa2a858910e3ac3b8")
declare cid=$(echo $POST_DATA | jq '.parameters.communication_id' | tr -d '"')

# get IDs of patent documents
declare patentids=$(echo $POST_DATA | jq '.parameters.documents[] | select(.source == "PATENT SERVER") | .document_id' | tr -d '"')
# get docid sectionid text lines
declare docs=$(./external_services/patent_server.sh $patentids 2>/dev/null | jq '.[] | .doc_id + (" T " + .title, " A " + .abstract)' | tr -d '"')

declare pubmedids=$(echo $POST_DATA | jq '.parameters.documents[] | select(.source == "PubMed") | .document_id' | tr -d '"')
        docs=$(echo "$docs" "$(./external_services/pubmed.sh $pubmedids 2>/dev/null | jq '.[] | .doc_id + (" T " + .title, " A " + .abstract)' | tr -d '"')")
declare pmcids=$(echo $POST_DATA | jq '.parameters.documents[] | select(.source == "PMC") | .document_id' | tr -d '"')
        #docs=$(echo "$docs" "$(./external_services/pmc.sh $pmcids 2>/dev/null | jq '.[] | .doc_id + (" T " + .title, " A " + .abstract)' | tr -d '"')")
declare results=$(echo -e "DOCUMENT_ID\tSECTION\tINIT\tEND\tSCORE\tANNOTATED_TEXT\tTYPE\tDATABASE_ID\n")
SAVEIFS=$IFS;
IFS=$'\n'
for i in $docs
do
    #echo $i
    IFS=$' '; arr=($i)
    text=$(echo ${arr[@]:2})
    # use ts
    #TASKID=$(ts ./process_document.sh  ${arr[@]:0:2} "$text")
    #declare task_results=$(ts -c $TASKID)
    declare task_results=$(./process_document.sh  ${arr[@]:0:2} "$text")
    results=$(echo -e "$results\n$task_results")
done
IFS=$SAVEIFS
# echo $(ts)
echo -e $results
# save annotations
declare responseurl=$(echo 'http://www.becalm.eu/api/saveAnnotations/TSV?apikey='$key'&communicationId='$cid)
echo -e $responseurl
curl -X POST --data "$results" $responseurl --header "Content-Type:text/tab-separated-values"
