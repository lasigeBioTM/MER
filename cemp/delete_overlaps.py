import sys

"""Delete overlaps of annotations in the same document in annotation files.

Use: python delete_overlaps.py [input_file_name] [output_file_name]

* If the one annotation is a subset of another, longer annotation, the smaller
one is deleted.
* If two annotations partially overlaps one another the smaller one is deleted.
If same length, one is deleted arbitrarily.
"""

in_filename = sys.argv[1]
out_filename = sys.argv[2]

with open(in_filename) as f:
    annots = map(lambda annot: annot.split('\t'), f.readlines())[1:]

annots_by_document = {}
for annot in annots:
    document_id = annot[0]

    if document_id not in annots_by_document.keys():
        annots_by_document[document_id] = []
    annots_by_document[document_id].append(annot)

for document_id in annots_by_document.keys():
    annots = annots_by_document[document_id]

    length_annots = len(annots)
    indexes_to_delete = []
    for i in range(length_annots):
        init_i = int(annots[i][2])
        end_i = int(annots[i][3])
        section_i = annots[i][1]
        annotated_text_i = annots[i][5]
        for j in range(length_annots):
            if j == i:
                continue
            init_j = int(annots[j][2])
            end_j = int(annots[j][3])
            section_j = annots[j][1]
            annotated_text_j = annots[j][5]

            if section_j != section_i:
                continue

            if init_j >= init_i and end_j <= end_i:
                indexes_to_delete.append(j)

            if (init_j < init_i and end_j < end_i and end_j > init_i) or (init_j > init_i and end_j > end_i and init_j < end_i):
                if len(annotated_text_i) > len(annotated_text_j):
                    indexes_to_delete.append(j)
                elif len(annotated_text_i) == len(annotated_text_j):
                    if i < j:
                        indexes_to_delete.append(j)

    new_annots = [annot for index, annot in enumerate(annots) if index not in indexes_to_delete]

    annots_by_document[document_id] = new_annots


with open(out_filename, 'w') as f:
    f.write('DOCUMENT_ID\tSECTION\tINIT\tEND\tSCORE\tANNOTATED_TEXT\tTYPE\tDATABASE_ID\n')
    for annots in annots_by_document.values():
        for annot in annots:
            f.write('\t'.join(annot))
