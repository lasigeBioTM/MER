#!/bin/bash

#set -x 
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
#declare key=$(echo "e2b88b40674b13e92fc6e41aa2a858910e3ac3b8")
declare key=$(echo "ad05c12336cc9c137f8010051ad0c2cc8f99bdff")
declare becalm_key=$(echo $POST_DATA | jq '.becalm_key')

#if [ $becalm_key = '"3deb66a13349fc7889549dfda065a3d8877ac04f"' ]; then
if [ $becalm_key = '"10924ad95a9800e21087271f08b1e360c2acbdbd"' ]; then
    declare method=$(echo $POST_DATA | jq '.method')
    if [ $method = '"getState"' ]; then
        declare serverstatus=$(echo 'Running')
        declare statuscode=$(echo '200')
        declare maxdocuments=$(echo '515')
        # send status response
        declare response=$(echo '{"status": '$statuscode',  "success": true,  "key":"'$key'",  "data": {"state":"'$serverstatus'", "version": "1", "version_changes": "first version", "max_analyzable_documents":"'$maxdocuments'"}}')
        echo $response
    
    elif [ $method = '"getAnnotations"' ]; then
        # ts -S 3 # set ts to run 3 parallel jobs
        # acknowledge request
        declare response=$(echo '{"status": 200, "success": true, "key":"'$key'"}')
        echo $response
        # process request
        #./process_request.sh "$POST_DATA" >> response_log.txt 2>&1 &       
        ./process_request.sh "$POST_DATA" >> response_log.txt 2>&1 &       
    fi
    
fi
exit 0
