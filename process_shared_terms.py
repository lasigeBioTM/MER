import os
import collections

"""Put all the terms that are shared between data files in a data file called
"UNKNOWN.txt" and delete them from the original files"""

# Don't want to process files used for testing purposes
documents_to_ignore = ['README.txt',
                       'ChEBI.txt',
                       'ChEMBL.txt',
                       'test_data.txt']

all_terms = []
for source in os.listdir('data/'):

    if source in documents_to_ignore:
        continue

    with open('data/' + source) as f:
        terms = f.readlines()
    all_terms += terms

shared_terms = [term for term, count in collections.Counter(all_terms).items() if count > 1]

# Write all shared terms to a new file
with open('data/UNKNOWN.txt', 'wb') as f:
    map(lambda term: f.write(term), shared_terms)

# Delete shared terms from the others data files
for source in os.listdir('data/'):

    if source in documents_to_ignore or source == 'UNKNOWN.txt':
        continue

    with open('data/' + source) as f:
        terms = f.readlines()
        non_shared_terms = [term for term in terms if term not in shared_terms]

    with open('data/' + source, 'wb') as f:
        map(lambda term: f.write(term), non_shared_terms)