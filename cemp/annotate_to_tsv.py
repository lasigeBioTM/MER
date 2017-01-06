import sys
import subprocess

# "test" or "training"
set_to_annotate = sys.argv[1]

becalm_tsv_header = 'DOCUMENT_ID\tSECTION\tINIT\tEND\tSCORE\tANNOTATED_TEXT\tTYPE\tDATABASE_ID\n'

final_tsv = ''
final_tsv += becalm_tsv_header

with open('{}_set.txt'.format(set_to_annotate)) as f:
    documents = f.readlines()

for document in documents:
    document_id, abstract, text = document.split('\t')

    annot_abstract_commant = 'cd ..; bash get_entities.sh {} {} "{}"'.format(document_id, 'A', abstract)
    annot_text_commant = 'cd ..; bash get_entities.sh {} {} "{}"'.format(document_id, 'T', text)

    final_tsv += subprocess.check_output(annot_abstract_commant, shell=True)
    final_tsv += subprocess.check_output(annot_text_commant, shell=True)

with open('{}_set_annots.tsv'.format(set_to_annotate), 'w') as f:
    f.write(final_tsv)
