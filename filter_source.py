import sys

# Filters common English words from the data source given as argument
# List of words downloaded from here, using the default values:
# http://app.aspell.net/create

source = sys.argv[1]

with open('data/english_words.txt') as f:
    common_words = set(map(lambda word: word.lower(), f.readlines())[44:])

with open('data/{}.txt'.format(source)) as f:
    pubchem_words = set(map(lambda word: word.lower(), f.readlines()))

filtered_pubchem_words = pubchem_words.difference(common_words)

with open('data/{}_filtered.txt'.format(source), 'w') as f:
    map(f.write, filtered_pubchem_words)
