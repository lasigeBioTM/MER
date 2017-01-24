#!/bin/bash

#set -x #debug
ts -S 3 > /dev/null 2>&1  # set ts to run 3 parallel jobs

declare POST_DATA=$2
declare key=$1

declare cid=$(echo $POST_DATA | jq '.parameters.communication_id' | tr -d '"')

timestamp() {
  date +"%Y-%m-%d_%H-%M-%S"
}


# get IDs of patent documents
declare patentids=$(echo $POST_DATA | jq '.parameters.documents[] | select(.source == "PATENT SERVER") | .document_id' | tr -d '"')
# get docid sectionid text lines
declare docs=$(./external_services/patent_server.sh $patentids 2>/dev/null | jq '.[] | .doc_id + (" T " + .title, " A " + .abstract)' | tr -d '"')

declare pubmedids=$(echo $POST_DATA | jq '.parameters.documents[] | select(.source == "PubMed") | .document_id' | tr -d '"')
        docs=$(echo "$docs" "$(./external_services/pubmed.sh $pubmedids 2>/dev/null | jq '.[] | .doc_id + (" T " + .title, " A " + .abstract)' | tr -d '"')")
declare pmcids=$(echo $POST_DATA | jq '.parameters.documents[] | select(.source == "PMC") | .document_id' | tr -d '"')
        #docs=$(echo "$docs" "$(./external_services/pmc.sh $pmcids 2>/dev/null | jq '.[] | .doc_id + (" T " + .title, " A " + .abstract)' | tr -d '"')")
declare results=$(echo -e "DOCUMENT_ID\tSECTION\tINIT\tEND\tSCORE\tANNOTATED_TEXT\tTYPE\tDATABASE_ID\n")
declare taskids=$(echo "")

SAVEIFS=$IFS;
IFS=$'\n'

# start jobs for each document abstract and title
for i in $docs
do
    #echo $i
    IFS=$' '; arr=($i)
    text=$(echo ${arr[@]:2})
    #declare task_results=$(./process_document.sh  ${arr[@]:0:2} "$text")
    # use ts
    TASKID=$(ts ./process_document.sh  ${arr[@]:0:2} "$text")
    taskids=$(echo "$taskids $TASKID")
done
IFS=$SAVEIFS

# wait until every job associated with this request is finished
while [ -n "$taskids" ]; do
    new_taskids= # temporary list to store unfinished jobs 
    for i in $taskids
    do
        # echo $(timestamp) $i $(ts -s $i) $taskids "/" $new_taskids >> response_log.txt 
	if [ $(ts -s $i) != 'finished'  ]; then
            declare new_taskids=$(echo "$new_taskids $i")
        else    
	    declare task_results=$(ts -c $i)
	    results=$(echo -e "$results\n$task_results")
        fi
    done 
    declare taskids=$(echo $new_taskids)
done

# echo $(ts)
echo -e $(timestamp) $results >> response_log.txt
# save annotations
declare responseurl=$(echo 'http://www.becalm.eu/api/saveAnnotations/TSV?apikey='$key'&communicationId='$cid)
echo -e $(timestamp) $responseurl >> response_log.txt
curl -X POST --data "$results" $responseurl --header "Content-Type:text/tab-separated-values" >> response_log.txt
