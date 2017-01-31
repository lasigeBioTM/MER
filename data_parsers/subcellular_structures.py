import csv

"""Uses "cellular components" subset of Gene Ontology"""

cell_components_names = []
with open('GO.csv') as csvfile:
    csvreader = csv.reader(csvfile)
    # Skip header
    csvreader.next()
    for go_entry in csvreader:

        if go_entry[19] != 'cellular_component':
            continue

        preferred_name = go_entry[1]
        cell_components_names.append(preferred_name)

        synonyms = go_entry[2].split('|')
        if synonyms[0] != '':
            cell_components_names += synonyms

cell_components_names = map(lambda name: name.lower(), cell_components_names)
cell_components_names = list(set(cell_components_names))

with open('../../data/go_cell_components.txt', 'w') as termsfile:
    map(lambda name: termsfile.write(name + '\n'), cell_components_names)
