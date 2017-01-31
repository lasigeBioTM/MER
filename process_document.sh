#!/bin/bash
#set -x
declare docid=$1
declare section=$2
declare text=$3

#SAVEIFS=$IFS; IFS=$(echo -en "")

# use remote machines
#declare results=$(ssh -i $ssh_key centos@$chemical_ip 'cd ~/IBELight/; ./get_entities.sh '$docid $section '"'$text'"' 'CHEMICAL 2>/dev/null')
#results=$results$'\n'$(ssh -i $ssh_key centos@$protein_ip 'cd ~/IBELight/; ./get_entities.sh '$docid $section '"'$text'"' 'PROTEIN 2>/dev/null')
#results=$results$'\n'$(ssh -i $ssh_key centos@$chemical_ip 'cd ~/IBELight/; ./get_entities.sh '$docid $section '"'$text'"' 'UNKNOWN 2>/dev/null')

# use local machine
declare results=
for i in $TYPES 
do
    #IFS=; type_results=$(./get_entities.sh $docid $section "$text" "$i" 2>/dev/null); results=$results$'\n'$type_results &
    IFS=; ./get_entities.sh $docid $section "$text" "$i" 2>/dev/null &
done
wait
#echo $results

