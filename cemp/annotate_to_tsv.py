import sys
import subprocess

'''
Annotates CEMP corpus to BioCalm TSV Format

python annotate_to_tsv [type_of_set]

type_of_set is "test" or "training", for example
'''


def escape_special_characters(string):
    '''Escape characters so that they can be used in bash command'''
    return string.replace('"', '\\"').replace('`', '\`')


set_to_annotate = sys.argv[1]
data_source = sys.argv[2]

becalm_tsv_header = 'DOCUMENT_ID\tSECTION\tINIT\tEND\tSCORE\tANNOTATED_TEXT\tTYPE\tDATABASE_ID\n'

annotatons_file = open('{}_{}_set_annots.tsv'.format(data_source, set_to_annotate), 'w')
annotatons_file.write(becalm_tsv_header)

with open('{}_set.txt'.format(set_to_annotate)) as f:
    documents = f.readlines()

for document in documents:
    document_id, title, abstract = document.split('\t')

    title = escape_special_characters(title)
    abstract = escape_special_characters(abstract)

    annot_title_commant = 'cd ..; bash get_entities.sh {} {} "{}" {}'.format(
        document_id, 'T', title, data_source
    )
    annot_abstract_commant = 'cd ..; bash get_entities.sh {} {} "{}" {}'.format(
        document_id, 'A', abstract, data_source
    )

    annotatons_file.write(subprocess.check_output(annot_title_commant, shell=True))
    annotatons_file.write(subprocess.check_output(annot_abstract_commant, shell=True))

annotatons_file.close()

print data_source + ' ok'
