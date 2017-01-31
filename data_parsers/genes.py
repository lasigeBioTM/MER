import csv

"""Data from NCBI Entrez Gene database"""

gene_names = []
with open('All_Data.gene_info') as tsvfile:
    csvreader = csv.reader(tsvfile, dialect='excel-tab')
    # Skip header and non gene line
    csvreader.next()
    csvreader.next()
    for gene in csvreader:

        symbol = gene[2]
        gene_names.append(symbol)

        synonyms = gene[4].split('|')
        if synonyms[0] != '-':
            gene_names += synonyms

        symbol_authority = gene[11]
        if symbol_authority != '-':
            gene_names.append(symbol_authority)

        other_designations = gene[13].split('|')
        if other_designations[0] != '-':
            gene_names += other_designations

gene_names = list(set(gene_names))

with open('../../data/ncbi_entrez_gene.txt', 'w') as termsfile:
    map(lambda name: termsfile.write(name + '\n'), gene_names)
