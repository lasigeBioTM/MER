#!/bin/bash

#set -x #debug
ts -S 3 > /dev/null 2>&1  # set ts to run 3 parallel jobs

declare POST_DATA=$2
export KEY=$1

export CID=$(echo $POST_DATA | jq '.parameters.communication_id' | tr -d '"')
export fakerequest=$(echo $POST_DATA | jq '.custom_parameters.fake')
timestamp() {
  date +"%Y-%m-%d_%H:%M:%S:%3N"
}
declare docs
echo $(timestamp) "get docs from sources" >> response_log.txt
# get IDs of patent documents
declare patentids=$(echo $POST_DATA | jq '.parameters.documents[] | select(.source == "PATENT SERVER") | .document_id' | tr -d '"')
# get docid sectionid text lines

if [ ${#patentids} -ge 1 ]; then
    docs=$docs\ $(./external_services/patent_server.sh $patentids 2>/dev/null | jq '.[] | .externalId + (" T " + .title, " A " + .abstractText)' | tr -d '"')
fi

declare abstractids=$(echo $POST_DATA | jq '.parameters.documents[] | select(.source == "ABSTRACT SERVER") | .document_id' | tr -d '"')
#echo $(timestamp) $abstractids >> response_log.txt
# get docid sectionid text lines
if [ ${#abstractids} -ge 1 ]; then
    docs=$docs\ $(./external_services/abstract_server.sh $abstractids 2>/dev/null | jq '.[] | .externalId + (" T " + .title, " A " + .text)' | tr -d '"')
fi

echo $(timestamp) "done"  >> response_log.txt

#declare pubmedids=$(echo $POST_DATA | jq '.parameters.documents[] | select(.source == "PubMed") | .document_id' | tr -d '"')
#        docs=$(echo "$docs" "$(./external_services/pubmed.sh $pubmedids 2>/dev/null | jq '.[] | .doc_id + (" T " + .title, " A " + .abstract)' | tr -d '"')")
#declare pmcids=$(echo $POST_DATA | jq '.parameters.documents[] | select(.source == "PMC") | .document_id' | tr -d '"')
        #docs=$(echo "$docs" "$(./external_services/pmc.sh $pmcids 2>/dev/null | jq '.[] | .doc_id + (" T " + .title, " A " + .abstract)' | tr -d '"')")
declare results=$(echo -e "DOCUMENT_ID\tSECTION\tINIT\tEND\tSCORE\tANNOTATED_TEXT\tTYPE\tDATABASE_ID\n")

echo "" > /tmp/${CID}.tasks
echo "" > /tmp/${CID}.completed
SAVEIFS=$IFS;
IFS=$'\n'
echo $(timestamp) "starting jobs"
# start jobs for each document abstract and title
for i in $docs
do
    #echo $i
    IFS=$' '; arr=($i)
    text=$(echo ${arr[@]:2})
    #declare task_results=$(./process_document.sh  ${arr[@]:0:2} "$text")
    # use ts
    TASKID=$(ts ./process_document.sh  ${arr[@]:0:2} "$text")
    #export TASKIDS=$TASKIDS\ $TASKID
    echo $TASKID >> /tmp/${CID}.tasks
    echo $(timestamp) "queued " $TASKID >> response_log.txt
    ( ts -w $TASKID ; echo "$TASKID" >> /tmp/${CID}.completed ; ./send_response.sh $TASKID ) & 
done

echo "DONE" >> /tmp/${CID}.tasks
IFS=$SAVEIFS

