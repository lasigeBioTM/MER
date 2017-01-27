#!/bin/bash

cd data

# Delete old files

rm "!(README.txt)"

# Download virgin data files from Google Drive

wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=0B5R2YTHDeD6sb0U2R0JCeEF3LVk' -O cells.txt
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=0B5R2YTHDeD6sTGNVUmFnanVDQkU' -O alpha-amylase.txt
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=0B5R2YTHDeD6sS1hKMXFpNXhfS0E' -O ChEBI.txt
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=0B5R2YTHDeD6sUG5WOXl2dzN4V00' -O ChEMBL.txt
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=0B5R2YTHDeD6sVVQ1UlJEYWxGZWc' -O CHEMICAL.txt
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=0B5R2YTHDeD6scnRXVGllRno3QUU' -O DISEASE.txt
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=0B5R2YTHDeD6sUzVydDNScXQ1MzA' -O GENE.txt
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=0B5R2YTHDeD6sVVh0a3E5WndXbHM' -O PROTEIN.txt
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=0B5R2YTHDeD6scFNmZl9pMmktTVE' -O subcellular_structures.txt

cd ..

# Remove duplicates from each data file

python remove_duplicates.py

# Put all the terms that are shared between data files in a data file called "UNKNOWN.txt" and delete them from the original files

python process_shared_terms.py

# Process all data files

cd data

ls | grep -Ev 'README.*|*_words?1?2?.txt' | xargs -l ../produce_data_files.sh

cd ..
