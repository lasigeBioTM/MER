#!/bin/bash

###############################################################################
#                                                                             #
# Licensed under the Apache License, Version 2.0 (the "License"); you may     #
# not use this file except in compliance with the License. You may obtain a   #
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0           #
#                                                                             #
# Unless required by applicable law or agreed to in writing, software         #
# distributed under the License is distributed on an "AS IS" BASIS,           #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    #
# See the License for the specific language governing permissions and         #
# limitations under the License.                                              #
#                                                                             #
###############################################################################
#                                                                             #
# Software developed based on the work published in the following articles:   #
# - F. Couto, L. Campos, and A. Lamurias, MER: a minimal named-entity         #
#   recognition tagger and annotation server,                                 #
#   in BioCreative V.5 Challenge Evaluation, 2017                             #
#   www.biocreative.org/media/store/files/2017/BioCreative_V5_paper18.pdf     #
#                                                                             #
# @authors F. Couto, L. Campos, and A. Lamurias                               #
###############################################################################

# Uncomment the line below to enable debug mode
# set -x

# Configuration variables
use_stopwords=1        # Flag to indicate whether to use stopwords
min_firstword=3        # Minimum number of alpha characters in the first word for matching
stopwords=stopwords.txt # File containing the list of stopwords

# Preserve the original IFS (Internal Field Separator) and set IFS to an empty string
OIFS=$IFS
IFS=""

# Read the input text and data source from the script arguments
original_text=$(tr '\n\r' ' ' <<< "$1")
data_source=$2

# Validate the input parameters
if [[ -z $original_text || -z $data_source ]]; then
    echo "Usage: get_entities.sh <text> <lexicon>"
    echo "Check the examples in the test.sh file"
    exit 1
fi

# Pre-process the input text
# Convert text to lowercase for case-insensitive matching
text=$(tr '[:upper:]' '[:lower:]' <<< "$original_text")
# Replace various delimiters with a space
text=$(sed "s/[:,.;-\(\)]/ /g" <<< "$text")
# Replace non-alphanumeric characters with a dot
text=$(sed "s/[^[:alnum:][:space:]()]/./g" <<< "$text")
# Remove multiple whitespace and replace with a single space
text=$(sed -e 's/[[:space:]()@]\+/ /g' <<< "$text")

# Remove stopwords if the flag is set
if [ $use_stopwords -eq 1 ]; then
    text=$(tr ' ' '\n' <<< "$text" | grep -v -w -f "$stopwords" | tr '\n' ' ')
fi

# Remove leading and trailing whitespace
text=$(sed -e 's/^ *//' -e 's/ *$//' <<< "$text")

# Separate all words in the text with pipes
piped_text=$(sed -e 's/ \+/|/g' <<< "$text")

# Create combinations of pairs of consecutive words, starting at the first word
piped_pair_text1=$(sed -e 's/\([^ ]\+ \+[^ ]\+\) /\1|/g' <<< "$text XXX" | sed 's/|[^|]*$//')

# Create combinations of pairs of consecutive words, starting at the second word
piped_pair_text2=$(sed -e 's/\([^ ]\+ \+[^ ]\+\) /\1|/g' <<< "XXX $text XXX" | sed 's/^[^|]*|//' | sed 's/|[^|]*$//')

# Combine both previous combinations of pairs of words
piped_pair_text=$piped_pair_text1'|'$piped_pair_text2

# Function to find the start and end position of each matched term
get_matches_positions () {
    local matches=$1
    local results=''
    local matching_text=' '
    local new_matching_text="$original_text"

    # Add matches with multiple whitespace
    matches=$(sed -e 's/ / +/g' <<< "$matches")

    # Loop until there are no changes in new_matching_text
    while [ "$new_matching_text" != "$matching_text" ]; do
        # Avoid mixing word1 and word2 by escaping dots
        matches=$(sed 's/\./\[^ \]/g' <<< "$matches")
        matching_text=$new_matching_text

        # Find the start and end position of the first match
        local result
        result=$(awk 'BEGIN {IGNORECASE = 1}
            match($0,/'"$matches"'/){
                if (substr($0, RSTART-1, 1) ~ "[^[:alnum:]@-]" && substr($0, RSTART+RLENGTH, 1) ~ "[^[:alnum:]@-]")
                    print RSTART-2 "\t" RSTART-2+RLENGTH "\t" substr($0, RSTART, RLENGTH)
            }' <<< " $matching_text ")

        # Mask the match in the matching text to avoid full overlapping matches
        local match_hidden
        match_hidden=$(awk 'BEGIN {IGNORECASE = 1}
            match($0,/'"$matches"'/){print substr($0, RSTART, RLENGTH)}' <<< " $matching_text " | tr '[:alnum:]' '@')
        new_matching_text=$(awk 'BEGIN {IGNORECASE = 1} {sub(/'"$matches"'/,"'"$match_hidden"'",$0)}1' <<< "$matching_text")

        if [ ${#result} -ge 2 ]; then
            results=$results$'\n'$result
        fi
    done
    get_matches_positions_result=$results
}

# Function to match the one-word pattern in the lexicon
get_entities_source_word1 () {
    local labels=$1
    get_entities_source_word1_result=''

    if [ ${#piped_text} -ge 2 ]; then
        local matches
        matches=$(egrep '^('"$piped_text"')$' "$labels" | tr '\n' '|' | sed 's/|[[:space:]]*$//')
        if [ ${#matches} -ge 2 ]; then
            get_matches_positions "$matches"
            get_entities_source_word1_result=$get_matches_positions_result
        fi
    fi
}

# Function to match the two-word pattern in the lexicon
get_entities_source_word2 () {
    local labels=$1
    get_entities_source_word2_result=''

    if [ ${#piped_pair_text} -ge 2 ]; then
        local matches
        matches=$(egrep '^('"$piped_pair_text"')$' "$labels" | tr '\n' '|' | sed 's/|[[:space:]]*$//')
        if [ ${#matches} -ge 2 ]; then
            get_matches_positions "$matches"
            get_entities_source_word2_result=$get_matches_positions_result
        fi
    fi
}

# Function to match the two-word pattern in the lexicon files for two-first-words and more-words
get_entities_source_words () {
    local labels2=$1
    local labels=$2
    get_entities_source_words_result=''

    if [ ${#piped_pair_text} -ge 2 ]; then
        # Find the two-first-word matches
        local matches
        matches=$(egrep '^('"$piped_pair_text"')$' "$labels2" | egrep '[[:alpha:]]{'$min_firstword',}' | tr '\n' '|' | sed 's/|[[:space:]]*$//')
        if [ ${#matches} -ge 2 ]; then
            # Find the more-words matches based on the previous matches
            local fullmatches
            fullmatches=$(egrep '^('"$matches"')' "$labels" | tr '\n' '|' | sed 's/|[[:space:]]*$//')
            get_matches_positions "$fullmatches"
            get_entities_source_words_result=$get_matches_positions_result
        fi
    fi
}

# Function to launch jobs for each of the 3 types of matches
get_entities_source () {
    local source=$1
    cd data/ || exit
    local result1 result2 result3

    get_entities_source_word1 "$source"_word1.txt
    result1=$get_entities_source_word1_result

    get_entities_source_word2 "$source"_word2.txt
    result2=$get_entities_source_word2_result

    get_entities_source_words "$source"_words2.txt "$source"_words.txt
    result3=$get_entities_source_words_result

    # Check if all the results are empty. If yes, terminate the function.
    if [[ -z $result1 && -z $result2 && -z $result3 ]]; then
        cd ..
        return
    fi

    # Combine the results from the 3 types of matches
    local result=$result1$'\n'$result2$'\n'$result3
    result=$(sed '{/^$/d}' <<< "$result" | sort -n -k1,1 ) # Remove empty lines

    if [ -e "$source"_links.tsv ]; then
        while read -r line; do
            local label=$(cut -d$'\t' -f3- <<< "$line")
            local text=$(sed "s/[^[:alnum:][:space:]()]/./g" <<< "$label") # Replace special characters
            text=$(sed -e 's/[[:space:]()@]\+/ /g' <<< "$text") # Remove multiple whitespace
            text=$(sed -e 's/\.$//' -e 's/\. / /g' <<< "$text") # Remove full stops
            text=$(tr '[:upper:]' '[:lower:]' <<< "$text") # Make text lowercase
            text=$(sed -e 's/^ *//' -e 's/ *$//' <<< "$text") # Remove leading and trailing whitespace
            local link=$(egrep -m 1 "^$text"$'\t' "$source"_links.tsv | cut -f2)
            echo -e "$line\t$link"
        done <<< "$result"
    else 
        echo "$result"
    fi
    cd ..
}

get_entities_source "$data_source"
IFS=$OIFS
