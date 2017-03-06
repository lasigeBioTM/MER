import os

"""Lowercase and remove trailing white spaces of all terms from each data file
   in data/ folder"""

for source in os.listdir('data/'):

    if source == 'README.txt':
        continue

    with open('data/' + source) as f:
        terms = f.readlines()

    normalized_terms = map(lambda term: term.lower().strip(), terms)

    with open('data/' + source, 'wb') as f:
        map(lambda term: f.write(term + '\n'), normalized_terms)
