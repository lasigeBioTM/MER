import os

"""Removes duplicate terms from each data file in data/ folder"""

for source in os.listdir('data/'):

    if source == 'README.txt':
        continue

    with open('data/' + source) as f:
        terms = f.readlines()

    no_duplicates = list(set(terms))

    with open('data/' + source, 'wb') as f:
        map(lambda term: f.write(term), no_duplicates)
