#!/bin/bash

IFS=""

correct_result='0	9	α-maltose	http://purl.obolibrary.org/obo/CHEBI_18167
14	28	nicotinic acid	http://purl.obolibrary.org/obo/CHEBI_15940
48	62	nicotinic acid	http://purl.obolibrary.org/obo/CHEBI_15940
48	79	nicotinic acid D-ribonucleotide	http://purl.obolibrary.org/obo/CHEBI_15763'


(cd data; ../produce_data_files.sh lexicon.txt)
result=$(./get_entities.sh "α-maltose and nicotinic acid was found, but not nicotinic acid D-ribonucleotide" lexicon)

if diff -y <(echo $correct_result) <(echo $result); then
 echo "Great you are ready to go!"
else
 echo "Sorry, something is not working well!"
fi
