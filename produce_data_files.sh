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

SAVEIFS=$IFS; IFS=$(echo -en "");

min_entity_size_alpha=3
max_entity_size_digit=5
# set -x #debug

filename=${1%.*}

	if [[ $1 == 'wordnet-hyponym.rdf' ]]; then
	    grep -F '<rdf:Description rdf:about' $1 | \
			sed 's/^.*synset-//' | \
			sed 's/-[^-]*-[0-9]*".*$//' | \
			tr '_' ' '  | \
			tr '[:upper:]' '[:lower:]' > $filename.txt 

	elif [[ $1 =~ \.(owl|rdf|xml)$ ]]; then # with entity linking

	    if [[ $1 = *".owl" ]]; then
			labels=$(grep -F -e 'owl:Class rdf:about' -e 'rdfs:label' -e 'oboInOwl:hasExactSynonym' -e 'oboInOwl:hasRelatedSynonym'  $1  | \
						 tr '\n' ' ' | \
						 sed -e 's/<owl:Class/\n<owl:Class/g'  | \
						 grep '^<owl:Class' | \
						 sed 's/rdf:about="\([^"]*\)"/>\1</' | \
						 awk -F'[<>]' '{for(i=NF-2;i>4;i=i-4)printf "%s\t%s \n",$i,$3;}')
	    elif [[ $1 = *".rdf" ]]; then # radlex.rdf
			labels=$(grep -B 1 -F -e '<Literal xml:lang="en">' radlex.rdf | \
						 tr '\n' ' ' | \
						 sed -e 's/<AbbreviatedIRI>:/\n<AbbreviatedIRI>/g' | \
						 grep -v -E '<Literal xml:lang="en">RID[0-9]+<' | \
						 awk -F'[<>]' '{printf "%s\thttp://radlex.org/RID/%s \n",$7,$3;}')
	    elif [[ $1 = *".xml" ]]; then # decs.xml #-e '<QualifierUI>'
			labels=$(grep -A 3 -E -e '<DescriptorUI>' $1 | \
						 grep -F -e 'UI>' -e '<![CDATA' | \
						 tr '\n' ' ' | \
						 sed -e 's/<[^>/]*UI>/\n<UI>/g' | \
						 tr '[]' '<>' | \
						 awk -F'[<>]' '{printf "%s\thttps://decs.bvsalud.org/ths/?filter=ths_regid&q=%s \n",$8,$3;}')
	    fi
	    
	    echo "$labels" | sed -r 's/([^\t]+)/\L\1/' | sort -k1,1 -t$'\t' | uniq > $filename\_links.tsv
	    
	    cut -f1 $filename\_links.tsv > $filename.txt 
	fi
    
egrep "[[:alpha:]]{$min_entity_size_alpha,}" $filename.txt >  $filename.aux1
egrep -v "[[:digit:]]{$max_entity_size_digit,}" $filename.aux1 >  $filename.aux2

sed -e 's/^ *//' -e 's/ *$//' $filename.aux2 > $filename.aux3 # remove leading and trailing whitespace
sed -e 's/[[:space:]]\+/ /' $filename.aux3 >  $filename.aux4 # remove multiple whitespace
awk '!a[$0]++' $filename.aux4 > $filename.aux5 # remove duplicate lines

echo '================'
sed 's/[^[:alpha:][:digit:][:space:]]/./g' $filename.aux5 | tr '[:upper:]' '[:lower:]' > $filename.aux

egrep '^[^ ]*$' $filename.aux > $filename'_word1.txt'
tail $filename'_word1.txt'
echo '================'

egrep '^[^ ]+ [^ ]+$'  $filename.aux > $filename'_word2.txt'
tail $filename'_word2.txt' 
echo '================'

egrep ' [^ ]+ ' $filename.aux > $filename'_words.txt' 
tail $filename'_words.txt' 
echo '================'

egrep -o "^[^ ]+ [^ ]+"  $filename'_words.txt' | awk '!a[$0]++' > $filename'_words2.txt'
tail $filename'_words2.txt' 
echo '================'

rm -f $filename.aux*


