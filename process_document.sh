#!/bin/bash
#set -x
declare docid=$1
declare section=$2
declare text=$3

SAVEIFS=$IFS; IFS=$(echo -en "")

# use remote machines
#declare results=$(ssh -i $ssh_key centos@$chemical_ip 'cd ~/IBELight/; ./get_entities.sh '$docid $section '"'$text'"' 'CHEMICAL 2>/dev/null')
#results=$results$'\n'$(ssh -i $ssh_key centos@$protein_ip 'cd ~/IBELight/; ./get_entities.sh '$docid $section '"'$text'"' 'PROTEIN 2>/dev/null')
#results=$results$'\n'$(ssh -i $ssh_key centos@$chemical_ip 'cd ~/IBELight/; ./get_entities.sh '$docid $section '"'$text'"' 'UNKNOWN 2>/dev/null')

# use local machine
declare results=$(./get_entities.sh $docid $section "$text" "CHEMICAL" 2>/dev/null)
results=$results$'\n'$(./get_entities.sh $docid $section "$text" "PROTEIN" 2>/dev/null)
results=$results$'\n'$(./get_entities.sh $docid $section "$text" "DISEASE" 2>/dev/null)
results=$results$'\n'$(./get_entities.sh $docid $section "$text" "GENE" 2>/dev/null)
results=$results$'\n'$(./get_entities.sh $docid $section "$text" "SUBCELLULAR_STRUCTURE" 2>/dev/null)
results=$results$'\n'$(./get_entities.sh $docid $section "$text" "CELL_LINE_AND_CELL_TYPE" 2>/dev/null)
results=$results$'\n'$(./get_entities.sh $docid $section "$text" "UNKNOWN" 2>/dev/null)
echo $results

