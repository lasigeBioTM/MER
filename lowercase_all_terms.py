import os

"""Lowercase all terms from each data file in data/ folder"""

for source in os.listdir('data/'):

    if source == 'README.txt':
        continue

    with open('data/' + source) as f:
        terms = f.readlines()

    lowercase_terms = map(lambda term: term.lower(), terms)

    with open('data/' + source, 'wb') as f:
        map(lambda term: f.write(term), lowercase_terms)
