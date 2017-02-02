
declare fake=$1
declare TASKID=$2

timestamp() {
  date +"%Y-%m-%d_%H:%M:%S:%3N"
}
#echo $(timestamp) $TASKID $(ts -s $TASKID) $TASKIDS "/" $(cat /tmp/$CID) >> response_log.txt 
# check if all tasks have been added to the file
declare status=$(tail -1 /tmp/${CID}.tasks)
if [[ $status != "DONE" ]]; then
    #echo $(timestamp) $TASKID $status >> response_log.txt
    exit 0
fi
#echo $(timestamp) $TASKIDS $status >> response_log.txt
# ignore last line of tasks file because it should be DONE
declare sorted_completed=$(cat "/tmp/${CID}.completed" | sort -g)
declare all_tasks=$(head -n -1 "/tmp/${CID}.tasks" | sort -g)

# wait until every job associated with this request is finished
# check if all tasks have been completed
#echo $(timestamp) $all_tasks >> response_log.txt
IFS=
if [ $sorted_completed = $all_tasks ]; then
    echo $(timestamp) "all tasks completed" >> response_log.txt
    declare results=$(echo -e "DOCUMENT_ID\tSECTION\tINIT\tEND\tSCORE\tANNOTATED_TEXT\tTYPE\tDATABASE_ID\n")
    IFS=$'\n'
    for i in $all_tasks
    do
        declare task_results=$(ts -c $i)
        # echo $(timestamp) "results:" $i $task_results >> response_log.txt
        results=$(echo -e "$results\n$task_results")
    done
    echo -e $(timestamp) $(echo "$results" | wc -l ) $results >> response_log.txt
    # save annotations
    declare responseurl=$(echo 'http://www.becalm.eu/api/saveAnnotations/TSV?apikey='$KEY'&communicationId='$CID)
    echo $(timestamp) $responseurl >> response_log.txt
    if [[ $fakerequest != "true" ]]; then
        echo -e "$results" | curl -X POST -H "Content-Type:text/tab-separated-values; charset=UTF-8" --data-binary @- $responseurl >> response_log.txt 2>&1
        echo "" >> response_log.txt
    fi
    declare END=$(date +%s.%N);
    echo $(timestamp) "time elapsed:" $(echo "$END - $START" | bc -l ) >> response_log.txt
    #    echo "fake request!" >> response_log.txt
#else
#    echo $(timestamp) "completed:" $sorted_completed  >> response_log.txt 
#    echo $(timestamp) "tasks:" $(echo $TASKIDS | tr " " "\n")  >> response_log.txt
fi
