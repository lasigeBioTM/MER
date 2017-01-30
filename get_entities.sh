#!/bin/bash

# set -x #debug

declare document_id=$1
declare section=$2
declare original_text=$3
declare data_source=$4

# Process text
declare text=${3,,} # Make text lowercase so the system is case insensitive
text=$(sed "s/[^[:alnum:][:space:]()]/./g" <<< "$text") # Replace special characters
text=$(sed -e 's/[[:space:]()@]\+/ /g' <<< $text) # remove multiple whitespace
text=$(sed -e 's/\.$//' -e 's/\. / /g' <<< $text) # remove full stops
text=$(tr ' ' '\n' <<< $text | grep -v -w -f stopwords.txt | tr '\n' ' ') # Remove stopwords
# | egrep '[[:alpha:]]{3,}'  and words with less than 3 characters
text=$(sed -e 's/^ *//' -e 's/ *$//' <<< $text) # Remove leading and trailing whitespace

# Separates all the words in the text by pipes
declare piped_text=$(sed -e 's/ \+/|/g' <<< $text)

# Creates all combinations of pairs of consecutive words in the text.
declare piped_pair_text1=$(sed -e 's/\([^ ]\+ \+[^ ]\+\) /\1|/g' <<< $text" XXX" | sed 's/|[^|]*$//')
declare piped_pair_text2=$(sed -e 's/\([^ ]\+ \+[^ ]\+\) /\1|/g' <<< "XXX "$text" XXX"| sed 's/^[^|]*|//' | sed 's/|[^|]*$//')
declare piped_pair_text=$piped_pair_text1'|'$piped_pair_text2


declare get_matches_positions_result=''
get_matches_positions () {
	local matches=$1	
	local results=''
	local matching_text=' '
	local new_matching_text=$original_text
	while [ "$new_matching_text" != "$matching_text" ];
	do
		matching_text=$new_matching_text
		local result=$(awk 'BEGIN {IGNORECASE = 1} 
			match($0,/'$matches'/){
				if (substr($0, RSTART-1, 1) ~ "[^[:alnum:]@]" && substr($0, RSTART+RLENGTH, 1) ~ "[^[:alnum:]@]")
						print "'$document_id'" "\t" \
							  "'$section'" "\t"  \
							  RSTART-2 "\t" \
							  RSTART-2+RLENGTH "\t" \
							  1-1/log(RLENGTH) "\t" \
							  substr($0, RSTART, RLENGTH) "\t" \
							  "'$data_source'" "\t" \
							  "1"}' <<< " $matching_text ")
		local match_hidden=$(awk 'BEGIN {IGNORECASE = 1} 
								match($0,/'$matches'/){print substr($0, RSTART, RLENGTH)}' <<< " $matching_text " | tr '[:alnum:]' '@')
		
		#$(awk -F $'\t' '' <<< $result | )  # to have overlaps: sed 's/[:alnum:]/@/1'
		new_matching_text=$(awk 'BEGIN {IGNORECASE = 1} {sub(/'$matches'/,"'$match_hidden'",$0)}1' <<< $matching_text)		
		if [ ${#result} -ge 2 ]; then 
			results=$results$'\n'$result	
		fi
	done
	get_matches_positions_result=$results;
}
	
declare get_entities_source_word1_result=''
get_entities_source_word1 () {
	local labels=$1
	get_entities_source_word1_result=''
	if [ ${#piped_text} -ge 2 ]; then
		local matches=$(egrep '^('$piped_text')$' $labels |  tr '\n' '|' | sed 's/|[[:space:]]*$//')
		if [ ${#matches} -ge 2 ]; then
			get_matches_positions $matches
			get_entities_source_word1_result=$get_matches_positions_result
		fi
	fi
}

declare get_entities_source_word2_result=''
get_entities_source_word2 () {
	local labels=$1
	get_entities_source_word2_result=''
	if [ ${#piped_pair_text} -ge 2 ]; then
		local matches=$(egrep '^('$piped_pair_text')$' $labels |  tr '\n' '|' | sed 's/|[[:space:]]*$//')
		if [ ${#matches} -ge 2 ]; then
			get_matches_positions $matches
			get_entities_source_word2_result=$get_matches_positions_result
		fi
	fi
}

declare get_entities_source_words_result=''
get_entities_source_words () {
	local labels2=$1
	local labels=$2
	get_entities_source_words_result=''
	if [ ${#piped_pair_text} -ge 2 ]; then
		local matches=$(egrep '^('$piped_pair_text')$' $labels2 | egrep '[[:alpha:]]{5,}' | tr '\n' '|' | sed 's/|[[:space:]]*$//' )
        if [ ${#matches} -ge 2 ]; then
		    local fullmatches=$(egrep '^('$matches')' $labels |  tr '\n' '|' | sed 's/|[[:space:]]*$//')
			get_matches_positions $fullmatches
			get_entities_source_words_result=$get_matches_positions_result
		fi
	fi
}

declare get_entities_source_words_result=''
get_entities_source () {
	local source=$1
	# echo "== BEGIN SOURCE == $source =="
	cd data/

	SAVEIFS=$IFS; IFS=$(echo -en "");

 	local result1=$(get_entities_source_word1 $source\_word1.txt && echo $get_entities_source_word1_result &)

	local result2=$(get_entities_source_word2 $source\_word2.txt && echo $get_entities_source_word2_result &)

	local result3=$(get_entities_source_words $source\_words2.txt $source\_words.txt && echo $get_entities_source_words_result &)

	wait
	cd ..

	# Check if all the results are empty. If yes, terminate function.
	if [[ -z $result1 && -z $result2 && -z $result3 ]]; then
		return
	fi

	local result=$result1$'\n'$result2$'\n'$result3
	result=$(sed '{/^$/d}' <<< $result) # remove empty lines
	
	echo $result
	#echo "== END SOURCE =="
	}

get_entities_source $data_source
