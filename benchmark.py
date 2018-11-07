import os
import time
import glob
import subprocess
import unidecode
import requests
from ratelimit import limits, sleep_and_retry


##
## Requires:
## HPO corpus (GSC/ or GSCplus - download from lasigeBioTM/IHP)
## MER (running locally and on an external server) - lasigeBioTM/MER
## Multifast - http://multifast.sourceforge.net/tool.php
## Bioportal API key
##

def get_hpo_documents(corpus=("GSCplus/documents/", "GSCplus/annotations/"), min_match_score=0, mapto="hpo"):
    docs = {}
    entities = {}
    ontology_ids = {}
    corpus_dir, annotations_dir = corpus
    docs_list = os.listdir(corpus_dir)
    documents_entity_list = {}  # docID -> entity_list
    docs_list = docs_list[:]
    for idoc, file in enumerate(docs_list):
        start_time = time.time()
        entity_list = {}  # entity -> candidate({name:,  id:, incount, outcount, links, etc}
        # print(file, idoc, len(docs_list))
        document_entities = set()
        #with open(corpus_dir + file) as f:
        #   text = f.readlines()[0]
        doc_entities = []
        doc_ontology_ids = []
        #print(corpus_dir, file)
        with open(corpus_dir + file) as f:
            text = f.read().strip()
            docs[file] = text
        with open(annotations_dir + file) as f:
            for line in f:
                values = line.split("\t")
                hpid, etext = values[1].strip().split(" | ")
                #hpid = hpid.replace("_", ":")
                #print(hpid)
                #if hpid in alt_id_to_id:
                #    hpid = alt_id_to_id[hpid]
                #    updated_id += 1
                start, end = values[0][1:-1].split("::")
                start, end = int(start), int(end)
                doc_entities.append((start, end, etext))
                doc_ontology_ids.append((start, end, hpid))
        entities[file] = doc_entities
        ontology_ids[file] = doc_ontology_ids
    return docs, entities, ontology_ids


def query_mer(doc_text):
    entities = set()
    ontoids = set()
    base_url = ""
    params = {"method": "getAnnotations",
              "becalm_key": "",
              "text": unidecode.unidecode(doc_text.replace('"', "'")),
              "types": ["hp"],
              "communication_id": 1}

    r = requests.post(base_url, json=params, headers={'Content-type': 'text/plain; charset=utf-8'})
    results = r.text
    if len(results.strip()) > 0:
        # print(results)
        for l in results.strip().split("\n"):
            v = l.split("\t")
            entities.add((int(v[0]), int(v[1]), v[2]))
            #ontoids.add((int(v[0]), int(v[1]), v[3].split("/")[-1]))
    return entities, ontoids


def query_local_mer(doc_text):
    entities = set()
    ontoids = set()
    os.chdir("MER/")
    cmd = './get_entities.sh "' + doc_text.replace('"', "") + '" hp'
    returned_output = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    #print(returned_output)
    results = returned_output.stdout.decode('utf-8')
    os.chdir("../")
    if len(results.strip()) > 0:
        #print(results)
        for l in results.strip().split("\n"):
            #print(l)
            v = l.split("\t")
            entities.add((int(v[0]), int(v[1]), v[2]))
            #ontoids.add((int(v[0]), int(v[1]), v[3].split("/")[-1]))
    return entities, ontoids

def query_local_aho(doc_text):
    entities = set()
    ontoids = set()
    #os.chdir("MER/")
    #cmd = ["echo", doc_text, "|", 'multifast', "-P", "MER/data/ahohp.txt", "-"]
    cmd = 'multifast -P MER/data/ahohp.txt -'
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, universal_newlines=True)
    #print(process.args)
    returned_output = process.communicate(input=doc_text)
    #print(returned_output)
    results = returned_output[0]
    if len(results.strip()) > 0:
        #print(results)
        for l in results.strip().split("\n"):
            if l.startswith("@"):
                #print(l)
                v = l.split(" ")
                start = int(v[0][1:]) - 1
                text = " ".join(v[1:])[1:-1]
                end = start + len(text)
                entities.add((start, end, text))
                #ontoids.add((int(v[0]), int(v[1]), v[3].split("/")[-1]))
    return entities, ontoids

#@sleep_and_retry
#@limits(calls=60, period=60)
def query_bioportal(doc_text):
    entities = set()
    ontoids = set()
    base_url = "http://data.bioontology.org/annotator"
    params = {"apikey": "",
              "text": doc_text,
              "ontologies": "HP"}

    r = requests.get(base_url, params)
    results = r.json()
    for annot in results:
        ontoid = annot["annotatedClass"]["@id"].split("/")[-1]
        for a in annot["annotations"]:
            entities.add((a["from"]-1, a["to"], doc_text[a["from"]-1:a["to"]]))
            ontoids.add((a["from"]-1, a["to"], ontoid))

    return entities, ontoids



def evaluate_results(gs, results):
    fp = len(results - gs)
    print("FP:", fp)
    fn = len(gs - results)
    print("FN:", fn)
    tp = len(results & gs)
    print("TP:", tp)
    print("precision:", tp / (tp + fp))
    print("recall:", tp / (tp + fn))


def get_gold_standard():
    docs, entities, ontoids = get_hpo_documents()
    gs_entities = set()
    gs_ontoids = set()
    for d in docs:
        for e in entities[d]:
            gs_entities.add((d, e[0], e[1], e[2]))
        for o in ontoids[d]:
            #print("ontoid", o)
            gs_ontoids.add((d, o[0], o[1], o[2]))
    return docs, gs_entities, gs_ontoids


def evaluate_local_mer(docs, gs_entities, gs_ontoids):
    print("MER (local)")
    # query mer
    mer_entities = set()
    mer_ontoids = set()
    for d in docs:
        doc_entities, doc_ontoids = query_local_mer(docs[d])
        for e in doc_entities:
            mer_entities.add((d, e[0], e[1], e[2]))
        for o in doc_ontoids:
            #if not o[2].startswith("PATO"):
            mer_ontoids.add((d, o[0], o[1], o[2]))


    print("entities evaluation")
    evaluate_results(gs_entities, mer_entities)
    #print("linking evaluation")
    #evaluate_results(gs_ontoids, mer_ontoids)
    return mer_entities, mer_ontoids


def evaluate_local_aho(docs, gs_entities, gs_ontoids):
    print("AHO")
    # query mer
    mer_entities = set()
    mer_ontoids = set()
    for d in docs:
        doc_entities, doc_ontoids = query_local_aho(docs[d])
        for e in doc_entities:
            mer_entities.add((d, e[0], e[1], e[2]))
        for o in doc_ontoids:
            #if not o[2].startswith("PATO"):
            mer_ontoids.add((d, o[0], o[1], o[2]))


    print("entities evaluation")
    evaluate_results(gs_entities, mer_entities)
    #print("linking evaluation")
    #evaluate_results(gs_ontoids, mer_ontoids)
    return mer_entities, mer_ontoids


def evaluate_mer(docs, gs_entities, gs_ontoids):
    print("MER")
    # query mer
    mer_entities = set()
    mer_ontoids = set()
    for d in docs:
        doc_entities, doc_ontoids = query_mer(docs[d])
        for e in doc_entities:
            mer_entities.add((d, e[0], e[1], e[2]))
        for o in doc_ontoids:
            #if not o[2].startswith("PATO"):
            mer_ontoids.add((d, o[0], o[1], o[2]))


    print("entities evaluation")
    evaluate_results(gs_entities, mer_entities)
    #print("linking evaluation")
    #evaluate_results(gs_ontoids, mer_ontoids)
    return mer_entities, mer_ontoids



def evaluate_bioportal(docs, gs_entities, gs_ontoids):
    print("BIOPORTAL")
    # query bioportal
    bp_entities = set()
    bp_ontoids = set()
    for d in docs:
        doc_entities, doc_ontoids = query_bioportal(docs[d])
        for e in doc_entities:
            bp_entities.add((d, e[0], e[1], e[2].lower()))
        for o in doc_ontoids:
            bp_ontoids.add((d, o[0], o[1], o[2]))


    print("entities evaluation")
    evaluate_results(gs_entities, bp_entities)

    print("linking evaluation")
    evaluate_results(gs_ontoids, bp_ontoids)
    return bp_entities, bp_ontoids

def main():
    docs, gs_entities, gs_ontoids = get_gold_standard()

    import time

    start = time.time()
    mer_entities, mer_ontoids = evaluate_local_aho(docs, gs_entities, gs_ontoids)
    end = time.time()
    print("Local AHO time", end - start)

    start = time.time()
    mer_entities, mer_ontoids = evaluate_local_mer(docs, gs_entities, gs_ontoids)
    end = time.time()
    print("Local MER time", end - start)
    start = time.time()

    mer_entities, mer_ontoids = evaluate_mer(docs, gs_entities, gs_ontoids)
    end = time.time()
    print("MER time", end - start)
    print("mer entities", len(mer_entities))

    start = time.time()
    bp_entities, bp_ontoids = evaluate_bioportal(docs, gs_entities, gs_ontoids)
    end = time.time()
    print("Bioportal time", end - start)
    print("bioportal entities", len(bp_entities))
    # entities found by BP but not MER
    mer_fns = (gs_entities & bp_entities) - mer_entities
    print(sorted(list(mer_fns), key=lambda x: x[0]))

if __name__ == "__main__":
    main()