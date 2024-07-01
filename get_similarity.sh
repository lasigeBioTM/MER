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
# Authors: F. Couto and A. Lamurias                                           #
###############################################################################

# Uncomment the following line to enable debug mode
# set -x #debug

# Usage example:
# ./get_entities.sh "α-maltose and nicotinic acid was found, but not nicotinic acid D-ribonucleotide" lexicon | ./get_similarity.sh Lin DiShIn ../DiShIn chebi.db

# Default values for the parameters
measure="Lin"              # Similarity measure to use
type="DiShIn"              # Type of ancestors to consider
dishin="../DiShIn"         # Path to the DiShIn tool
dishin_db="chebi.db"       # DiShIn database file

# Check if the first argument (measure) is provided, otherwise use the default value
if [ -z "$1" ]; then
    >&2 echo "No measure supplied, using $measure"
else
    measure=$1
fi

# Check if the second argument (type) is provided, otherwise use the default value
if [ -z "$2" ]; then
    >&2 echo "No ancestors type supplied, using $type"
else
    type=$2
fi

# Check if the third argument (DiShIn path) is provided, otherwise use the default value
if [ -z "$3" ]; then
    >&2 echo "No DiShIn path supplied, using $dishin"
else
    dishin=$3
fi

# Check if the fourth argument (DiShIn database file) is provided, otherwise use the default value
if [ -z "$4" ]; then
    >&2 echo "No DiShIn database file supplied, using $dishin_db"
else
    dishin_db=$4
fi

# Read the entire input from the pipeline
input=$(cat -)

# Extract the fourth column from the input, process each line to get the entity IDs
merlinks=$(echo -E "$input" | awk -F"\t" '{ print $4 }' | sed -E 's/^.*[/=]//')

# Process each match from the input
while read -r match; do
    maxsim=0           # Initialize the maximum similarity value
    t2=""              # Initialize the variable to store the most similar term
    t1=$(echo -E "$match" | awk -F"\t" '{ print $4 }' | sed -E 's/^.*[/=]//') # Extract the term from the match

    # Compare term t1 with each term in the list
    while read -r term2; do
        if [ "$t1" != "$term2" ]; then  # Ensure we don't compare the term with itself
            # Calculate the similarity using the DiShIn tool
            sim=$(python $dishin/dishin.py $dishin/$dishin_db $t1 $term2 | grep "^$measure" | grep "$type" | awk -F"\t" '{ print $4 }')

            # Use bc to compare the similarity value
            cmp=$(echo $sim'>'$maxsim | bc)
            if [ $cmp -eq 1 ]; then  # Update the maximum similarity and the corresponding term
                maxsim=$sim
                t2=$term2
            fi
        fi
    done <<<"$merlinks"

    # Output the match, most similar term, and maximum similarity
    echo -E "$match"$'\t'$t2$'\t'$maxsim
done <<<"$input"
