import csv
import re

"""Data from Protein Ontology"""


def delete_between_parenthesis(name):
    new_name = re.sub(' \(.*?\)', '', name)
    return new_name


protein_names = []
with open('PR.csv') as csvfile:
    csvreader = csv.reader(csvfile)
    # Skip header
    csvreader.next()
    for protein in csvreader:

        preferred_name = protein[1]
        protein_names.append(preferred_name)

        synonyms = protein[2].split('|')
        if synonyms[0] != '':
            protein_names += synonyms


protein_names = map(delete_between_parenthesis, protein_names)
protein_names = list(set(protein_names))

with open('../../data/protein_ontology.txt', 'w') as termsfile:
    map(lambda name: termsfile.write(name + '\n'), protein_names)
