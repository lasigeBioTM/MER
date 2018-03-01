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
# @authors F. Couto                                                           #
###############################################################################

# set -x #debug

OIFS=$IFS
IFS=$(echo -en "");

declare ontology=$1

# Check the given parameters
if [[ -z $ontology ]]; then
	echo "Usage: link_entities.sh <ontology>"
	echo "Check the examples in the test.sh file"
	exit
fi

# Pre-process the ontology
classes=$(tr '\n' ' ' < $ontology | sed -e 's/<owl:Class/\n<owl:Class/g' | grep '<owl:Class')

while read line
do
  label=$(sed -e 's/^[0-9 \t]*//' <<< $line) 
  link=$(egrep ">$label<\/rdfs:label>" <<< $classes | sed 's/^.*rdf:about="\([^"]*\).*$/\1/')
  if [[ -z $link ]]; then
      link=$(grep ">$label<\/oboInOwl:hasExactSynonym>" <<< $classes  | sed 's/^.*rdf:about="\([^"]*\).*$/\1/')
  fi
  echo -e "$link\t$label"
done 

IFS=$OIFS
