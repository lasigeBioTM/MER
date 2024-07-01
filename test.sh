#!/bin/bash

# Multiline string for correct result
correct_result=$'0\t9\tα-maltose\thttp://purl.obolibrary.org/obo/CHEBI_18167\n14\t28\tnicotinic acid\thttp://purl.obolibrary.org/obo/CHEBI_15940\n48\t62\tnicotinic acid\thttp://purl.obolibrary.org/obo/CHEBI_15940\n48\t79\tnicotinic acid D-ribonucleotide\thttp://purl.obolibrary.org/obo/CHEBI_15763'

# Ensure lexicon file is generated
(cd data && ../produce_data_files.sh lexicon.txt)

# Capture the result from the get_entities.sh script
result=$(./get_entities.sh "α-maltose and nicotinic acid was found, but not nicotinic acid D-ribonucleotide" lexicon)

# Compare the results
if diff -y <(echo "$correct_result") <(echo "$result"); then
  echo "Great you are ready to go!"
else
  echo "Sorry, something is not working well!"
fi
