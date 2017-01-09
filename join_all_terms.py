import os

unprocessed_files = filter(
    lambda filename: filename.find('word') == -1,
    os.listdir('data/.')
)

all_terms = []

for filename in unprocessed_files:
    with open('data/' + filename) as f:
        terms = f.readlines()

    all_terms += terms

# Remove duplicates
unique_terms = list(set(all_terms))

with open('data/all_terms.txt', 'w') as f:
    f.write(''.join(unique_terms))
