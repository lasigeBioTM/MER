#!/bin/bash
echo "HTTP/1.0 200 OK"

if [ "$REQUEST_METHOD" = "POST" ]; then
    if [ "$CONTENT_LENGTH" -gt 0 ]; then
        read -n $CONTENT_LENGTH POST_DATA <&0
    fi
    echo "Content-type: application/json"
    echo ""
else
    echo "Content-type: text/html"
    echo ""

    echo '<html>'
    echo '<head>'
    echo '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'
    echo '<title>IBELight</title>'
    echo '</head>'
    echo '<body>'
    echo 'IBELight'
    echo '</body>'
    echo '</html>'
    exit 0
fi

timestamp() {
  date +"%Y-%m-%d_%H-%M-%S"
}

echo $(timestamp) $POST_DATA >> request_log.txt
declare key=$(echo "e2b88b40674b13e92fc6e41aa2a858910e3ac3b8")
declare becalm_key=$(echo $POST_DATA | jq '.becalm_key')

if [ $becalm_key = '"3deb66a13349fc7889549dfda065a3d8877ac04f"' ]; then
    declare method=$(echo $POST_DATA | jq '.method')
    if [ $method = '"getState"' ]; then
        declare serverstatus=$(echo 'Running')
        declare statuscode=$(echo '200')
        declare maxdocuments=$(echo '515')
        # send status response
        declare response=$(echo '{"status": '$statuscode',  "success": true,  "key":"'$key'",  "data": {"state":"'$serverstatus'", "version": "1", "version_changes": "first version", "max_analyzable_documents":"'$maxdocuments'"}}')
        echo $response
    
    elif [ $method = '"getAnnotations"' ]; then
        # acknowledge request
        declare response=$(echo '{"status": 200, "success": true, "key":"'$key'"}')
        echo $response
        # process request
        declare cid=$(echo $POST_DATA | jq '.parameters.communication_id' | tr -d '"')
        declare docs=$(echo $POST_DATA | jq '.parameters.documents[] | .document_id + "," + .source' | tr -d '"')
        declare header=$(echo "DOCUMENT_ID\tSECTION\tINIT\tEND\tSCORE\tANNOTATED_TEXT\tTYPE\tDATABASE_ID\n")
        SAVEIFS=$IFS;
        IFS=$'\n'
        for i in $docs
        do
            # use ts
            IFS=',' TASKID=$(ts ./process_document.sh $i)
            declare results=$(ts -c $TASKID)
            # save annotations
            #declare results=$(echo $header $results)
            echo $results
            declare responseurl=$(echo 'http://www.becalm.eu/api/saveAnnotations/TSV?apikey='$key'&communicationId='$cid)
            echo $responseurl
            #curl -X POST --data "$results" $responseurl --header "Content-Type:text/tab-separated-values"
        done
        IFS=$SAVEIFS
    fi
    
fi
exit 0
