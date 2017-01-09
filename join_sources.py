import sys

sources = sys.argv[1:]
all_terms = []
for source in sources:
    with open('data/' + source + '.txt') as f:
        terms = f.readlines()
    all_terms += terms

# Remove duplicates
unique_terms = list(set(all_terms))

with open('data/{}.txt'.format('_'.join(sources)), 'w') as f:
    f.write(''.join(unique_terms))
