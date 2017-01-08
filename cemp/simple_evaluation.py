from Evaluator.Evaluator import Evaluator
import sys

'''Evaluation of prediction of IBELight.

python simple_evaluation.py [type_of_set]

type_of_set is "test" or "training", for example

The TSV prediction file and the gold annotations file given by the BioCalm team
have a different format, that's why I there is different code for each case

(Evaluator is a library that I've created some time ago to help me calculate
evaluation metrics. I used it here as an hack.)'''

set_to_evaluate = sys.argv[1]

# Prediction
with open('{}_set_annots.tsv'.format(set_to_evaluate)) as f:
    annots = map(lambda annot: annot.split('\t'), f.readlines())[1:]

annots_by_document = {}
for annot in annots:
    document_id = annot[0]
    match = annot[5]

    if document_id not in annots_by_document.keys():
        annots_by_document[document_id] = set()
    annots_by_document[document_id].add(match)

# Gold
with open('{}_set_gold_annots.tsv'.format(set_to_evaluate)) as f:
    annots = map(lambda annot: annot.split('\t'), f.readlines())

gold_annots_by_document = {}
for annot in annots:
    document_id = annot[0]
    match = annot[4]

    if document_id not in gold_annots_by_document.keys():
        gold_annots_by_document[document_id] = set()
    gold_annots_by_document[document_id].add(match)

ev_total = Evaluator(set([]), set([]))
documents_ids = list(set(gold_annots_by_document.keys() + annots_by_document.keys()))

for document_id in documents_ids:

    if document_id in annots_by_document.keys():
        annotations = annots_by_document[document_id]
    else:
        annotations = set([])

    if document_id in gold_annots_by_document.keys():
        gold_annotations = gold_annots_by_document[document_id]
    else:
        gold_annotations = set([])

    ev = Evaluator(gold_annotations, annotations)

    # print document_id
    # print "False Positives = {}".format(ev.false_positives())
    # print "False Negatives = {}".format(ev.false_negatives())
    # print

    ev_total._y_pred += ev._y_pred
    ev_total._y_true += ev._y_true

print "Total Precision = {}".format(ev_total.precision())
print "Total Recall = {}".format(ev_total.recall())
print "Total F1_score = {}".format(ev_total.f1_score())
