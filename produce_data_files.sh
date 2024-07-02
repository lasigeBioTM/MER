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
# Authors: F. Couto, L. Campos, and A. Lamurias                               #
###############################################################################

# Save and change IFS to handle filenames with spaces correctly
SAVEIFS=$IFS
IFS=$(echo -en "\n\b")

# Set parameters for entity size filtering
min_entity_size_alpha=3
max_entity_size_digit=5

# Input file from the first argument
FILE=$1

# Check if the file exists
if [[ ! -f "$FILE" ]]; then
    echo $'\n'"ERROR: File '$FILE' does not exist."$'\n'
    exit 1
fi

# Extract filename without extension
filename=${FILE%.*}

# Process wordnet-hyponym.rdf files
if [[ $FILE == 'wordnet-hyponym.rdf' ]]; then
    grep -F '<rdf:Description rdf:about' "$FILE" | \
    sed -E 's/^.*synset-//; s/-[^-]*-[0-9]*".*$//' | \
    tr '_' ' '  | \
    tr '[:upper:]' '[:lower:]' > "$filename.txt"

# Process .owl, .rdf, .xml files
elif [[ $FILE =~ \.(owl|rdf|xml)$ ]]; then
    # Process .owl files
    if [[ $FILE == *.owl ]]; then
        labels=$(grep -F -e 'owl:Class rdf:about' -e 'rdfs:label' -e 'oboInOwl:hasExactSynonym' -e 'oboInOwl:hasRelatedSynonym' "$FILE" | \
                 tr '\n' ' ' | \
                 sed -E 's/<owl:Class/\n<owl:Class/g' | \
                 grep '^<owl:Class' | \
                 sed -E 's/rdf:about="([^"]*)"/>\1</' | \
                 awk -F'[<>]' '{for(i=NF-2; i>4; i-=4) printf "%s\t%s\n", $i, $3}')
	
    #   Process radlex RDF/XML file 
    elif [[ $FILE == *.rdf ]]; then
	labels=$(grep -F -e 'rdf:about' -e 'Preferred_name xml:lang="en"'  $1  | \
		     tr '\n' ' ' | \
		     sed -e 's/rdf:about/\n<rdf:about/g'  | \
		     grep '^<rdf:about' | \
		     sed 's/rdf:about="\([^"]*\)"/>\1</' | \
		     awk -F'[<>]' '{for(i=NF-3;i>4;i=i-4)printf "%s\t%s \n",$i,$3;}')
	# Process radlex OWL file 
	#        labels=$(grep -B 1 -F -e '<Literal xml:lang="en">' "$FILE" | \
	    #                 tr '\n' ' ' | \
	    #                 sed -E 's/<AbbreviatedIRI>:/\n<AbbreviatedIRI>/g' | \
	    #                 grep -v -E '<Literal xml:lang="en">RID[0-9]+<' | \
	    #                 awk -F'[<>]' '{printf "%s\thttp://radlex.org/RID/%s\n", $7, $3}')

    # Process .xml files
    elif [[ $FILE == *.xml ]]; then
        language=${filename:12:3}
	labels=$(
	    grep -E -e '^  <DescriptorUI>' -e '<!\[CDATA\[' "$FILE" |
		awk '
	          BEGIN {	
	            RS="<";	
		    FS=">";	
		    ORS="\n"	
		    }
		      $1=="DescriptorUI" {
      			 # Extract descriptor ID and construct URL
      			 print "https://decs.bvsalud.org/ths/?filter=ths_regid&q="$2;
      			 flag=1
		      }
		      $1~/CDATA/&&flag==1 {
      			  # Extract descriptor label from CDATA block
      			  print "\t" $1 "|";
			  flag=0
		      }
	      ' | \
		tr -d '\n' | \
		tr '|' '\n' | \
		tr '[]' '||' | \
		sed  's/!|CDATA|\([^|]*\).*$/\1/g' | \
		awk -F'\t' '{
		    	   # Format output with label and URL
		       	   print $2"\t"$1
			  }'
	      )
    fi
    
    
    echo "$labels" | sed -r 's/([^\t]+)/\L\1/' | sort -k1,1 -t$'\t' | uniq > "$filename"_links.tsv
    
    # Extract first column for further processing
    cut -f1 "$filename"_links.tsv > "$filename.txt"
fi

# Filter lines based on alpha and digit criteria
egrep "[[:alpha:]]{$min_entity_size_alpha,}" "$filename.txt" > "$filename.aux1"
egrep -v "[[:digit:]]{$max_entity_size_digit,}" "$filename.aux1" > "$filename.aux2"

# Remove leading/trailing whitespace and collapse multiple spaces
sed -E 's/^ *| *$//g' "$filename.aux2" > "$filename.aux3"
sed -E 's/[[:space:]]+/ /g' "$filename.aux3" > "$filename.aux4"

# Remove duplicate lines
awk '!a[$0]++' "$filename.aux4" > "$filename.aux5"

# Output the results and create various files with different word combinations
echo '================'
sed 's/[^[:alpha:][:digit:][:space:]]/./g' "$filename.aux5" | tr '[:upper:]' '[:lower:]' > "$filename.aux"

# Create file with single words
egrep '^[^ ]*$' "$filename.aux" > "$filename"_word1.txt
tail "$filename"_word1.txt
echo '================'

# Create file with two-word combinations
egrep '^[^ ]+ [^ ]+$' "$filename.aux" > "$filename"_word2.txt
tail "$filename"_word2.txt
echo '================'

# Create file with multiple words
egrep ' [^ ]+ ' "$filename.aux" > "$filename"_words.txt
tail "$filename"_words.txt
echo '================'

# Create file with unique two-word combinations
egrep -o "^[^ ]+ [^ ]+" "$filename"_words.txt | awk '!a[$0]++' > "$filename"_words2.txt
tail "$filename"_words2.txt
echo '================'

# Clean up temporary files
rm -f "$filename.aux"*

# Restore original IFS
IFS=$SAVEIFS
