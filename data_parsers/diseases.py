import csv

"""Uses Human Disease Ontology data"""

disease_names = []
with open('DOID.csv') as csvfile:
    csvreader = csv.reader(csvfile)
    # Skip header
    csvreader.next()
    for disease in csvreader:

        preferred_name = disease[1]
        disease_names.append(preferred_name)

        synonyms = disease[2].split('|')
        if synonyms[0] != '':
            disease_names += synonyms

disease_names = map(lambda name: name.lower(), disease_names)
disease_names = list(set(disease_names))

with open('../../data/doid.txt', 'w') as termsfile:
    map(lambda name: termsfile.write(name + '\n'), disease_names)
