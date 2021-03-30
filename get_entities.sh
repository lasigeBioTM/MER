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

# set -x #debug
use_stopwords=1
min_firstword=3 #min number of alpha chars in first word
stopwords=stopwords.txt

OIFS=$IFS
IFS=$(echo -en "");

declare original_text=$(tr '\n\r' ' ' <<< $1)
declare data_source=$2

# Check the given parameters
if [[ -z $original_text || -z $data_source ]]; then
	echo "Usage: get_entities.sh <text> <lexicon>"
	echo "Check the examples in the test.sh file"
	exit
fi


# Pre-process the input text
declare text=$(tr '[:upper:]' '[:lower:]' <<< "$original_text") # Make text lowercase so the system is case insensitive
text=$(sed "s/[:,.;-\(\)]/ /g" <<< "$text") # Replace word delimiters by a space 
text=$(sed "s/[^[:alnum:][:space:]()]/./g" <<< "$text") # Replace special characters
text=$(sed -e 's/[[:space:]()@]\+/ /g' <<< $text) # remove multiple whitespace
# text=$(sed -e 's/\.$//' -e 's/\. / /g' <<< $text) # remove special characters at the end of word
if [ $use_stopwords -eq 1 ]; then
    text=$(tr ' ' '\n' <<< $text | grep -v -w -f $stopwords | tr '\n' ' ') # Remove stopwords
fi
# | egrep '[[:alpha:]]{3,}'  and words with less than 3 characters
text=$(sed -e 's/^ *//' -e 's/ *$//' <<< $text) # Remove leading and trailing whitespace
# Separates all the words in the text by pipes
declare piped_text
piped_text=$(sed -e 's/ \+/|/g' <<< $text)

# Creates all combinations of pairs of consecutive words in the text, staring at the first word 
declare piped_pair_text1
piped_pair_text1=$(sed -e 's/\([^ ]\+ \+[^ ]\+\) /\1|/g' <<< $text" XXX" | sed 's/|[^|]*$//')

# Creates all combinations of pairs of consecutive words in the text, staring at the second word
declare piped_pair_text2
piped_pair_text2=$(sed -e 's/\([^ ]\+ \+[^ ]\+\) /\1|/g' <<< "XXX $text XXX"| sed 's/^[^|]*|//' | sed 's/|[^|]*$//')

# Joins both previous combinations of pair of words
declare piped_pair_text=$piped_pair_text1'|'$piped_pair_text2

# Function that finds the start and end position of each given matched term 
declare get_matches_positions_result=''
get_matches_positions () {
	local matches=$1
	local results=''
	local matching_text=' '
	local new_matching_text=$original_text

	matches=$(sed -e 's/ / +/g' <<< $matches) # to add matches with multiple whitespace

	# While there are changes in the new_matching_text 

	while [ "$new_matching_text" != "$matching_text" ];
	do
		matches=$(sed 's/\./\[^ \]/g' <<< $matches) # avoid mixing word1 and word2...
		matching_text=$new_matching_text
		# Finds the start and end position of the first match
		local result
		result=$(awk 'BEGIN {IGNORECASE = 1}
			match($0,/'"$matches"'/){
				if (substr($0, RSTART-1, 1) ~ "[^[:alnum:]@-]" && substr($0, RSTART+RLENGTH, 1) ~ "[^[:alnum:]@-]")
						print RSTART-2 "\t" RSTART-2+RLENGTH "\t" substr($0, RSTART, RLENGTH)}' <<< " $matching_text ")
		# Masks the match in the matching text to avoid full overlapping matches

		local match_hidden
		match_hidden=$(awk 'BEGIN {IGNORECASE = 1}
					   match($0,/'"$matches"'/){print substr($0, RSTART, RLENGTH)}' <<< " $matching_text " | tr '[:alnum:]' '@')
		new_matching_text=$(awk 'BEGIN {IGNORECASE = 1} {sub(/'"$matches"'/,"'"$match_hidden"'",$0)}1' <<< $matching_text)
		if [ ${#result} -ge 2 ]; then
			results=$results$'\n'$result
		fi
	done
	get_matches_positions_result=$results;
}


# Function that matches the one-word pattern (piped_text) in the one-word file of the lexicon (labels)  
declare get_entities_source_word1_result=''
get_entities_source_word1 () {
	local labels=$1
	get_entities_source_word1_result=''
	if [ ${#piped_text} -ge 2 ]; then
		local matches
		matches=$(egrep '^('"$piped_text"')$' "$labels" |  tr '\n' '|' | sed 's/|[[:space:]]*$//')
		if [ ${#matches} -ge 2 ]; then
			get_matches_positions "$matches"
			get_entities_source_word1_result=$get_matches_positions_result
		fi
	fi
}

# Function that matches the two-word pattern (piped_pair_text) in the two-word file of the lexicon (labels)
declare get_entities_source_word2_result=''
get_entities_source_word2 () {
	local labels=$1
	get_entities_source_word2_result=''
	if [ ${#piped_pair_text} -ge 2 ]; then
		local matches
		matches=$(egrep '^('"$piped_pair_text"')$' "$labels" |  tr '\n' '|' | sed 's/|[[:space:]]*$//')
		if [ ${#matches} -ge 2 ]; then
			get_matches_positions "$matches"
			get_entities_source_word2_result=$get_matches_positions_result
		fi
	fi
}


# Function that matches the two-word pattern (piped_pair_text) in the two-first-words (labels2) and more-words (labels) files of the lexicon   
declare get_entities_source_words_result=''
get_entities_source_words () {
	local labels2=$1
	local labels=$2
	get_entities_source_words_result=''
	if [ ${#piped_pair_text} -ge 2 ]; then
		# finds the two-first-word matches
		local matches
		matches=$(egrep '^('"$piped_pair_text"')$' "$labels2" | egrep '[[:alpha:]]{'$min_firstword',}' | tr '\n' '|' | sed 's/|[[:space:]]*$//' )
        if [ ${#matches} -ge 2 ]; then
            # finds the more-words matches based on the previous matches
			local fullmatches
		    fullmatches=$(egrep '^('"$matches"')' "$labels" |  tr '\n' '|' | sed 's/|[[:space:]]*$//')
			get_matches_positions "$fullmatches"
			get_entities_source_words_result=$get_matches_positions_result
		fi
	fi
}

# Function that launches one job for each of the 3 types of matches
declare get_entities_source_words_result=''
get_entities_source () {
	local source=$1
	cd data/
	local result1
	local result2
	local result3
 	result1=$(get_entities_source_word1 "$source"_word1.txt && echo "$get_entities_source_word1_result" &)
	result2=$(get_entities_source_word2 "$source"_word2.txt && echo "$get_entities_source_word2_result" &)
	result3=$(get_entities_source_words "$source"_words2.txt "$source"_words.txt && echo $get_entities_source_words_result &)
	wait

	# Check if all the results are empty. If yes, terminate function.
	if [[ -z $result1 && -z $result2 && -z $result3 ]]; then
		return
	fi
	# combine the results from the 3 types of matches
	local result=$result1$'\n'$result2$'\n'$result3
	result=$(sed '{/^$/d}' <<< $result) # remove empty lines
	if [ -e "$source"_links.tsv ]; then
	    while read line
	    do
		#declare label=$(sed -e 's/^[0-9 \t]*//' <<< $line) 
		declare label=$(cut -d$'\t' -f3- <<< $line)
		declare text=$(sed "s/[^[:alnum:][:space:]()]/./g" <<< "$label") # Replace special characters
		text=$(sed -e 's/[[:space:]()@]\+/ /g' <<< $text) # remove multiple whitespace
		text=$(sed -e 's/\.$//' -e 's/\. / /g' <<< $text) # remove full stops
		text=$(tr '[:upper:]' '[:lower:]' <<< $text) # Make text lowercase so the system is case insensitive
		text=$(sed -e 's/^ *//' -e 's/ *$//' <<< $text) # Remove leading and trailing whitespace
		link=$(egrep -m 1 "^$text"$'\t' "$source"_links.tsv | cut -f2)
		echo -e "$line\t$link"
	    done <<< $result
	else 
	    echo "$result"
	fi
	cd ..
	}


get_entities_source "$data_source"
IFS=$OIFS
