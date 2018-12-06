# MER (Minimal Named-Entity Recognizer)

MER is a Named-Entity Recognition tool which given any lexicon and any input text returns the list of 
terms recognized in the text, including their exact location (annotations).

Given an ontology (owl file) MER is also able to link the entities to their classes.

More information about MER can be found in:
- MER: a Shell Script and Annotation Server for Minimal Named Entity Recognition and Linking, F. Couto and A. Lamurias, Journal of Cheminformatics, 10:58, 2018
[https://doi.org/10.1186/s13321-018-0312-9]
- MER: a Minimal Named-Entity Recognition Tagger and Annotation Server, F. Couto, L. Campos, and A. Lamurias, in BioCreative V.5 Challenge Evaluation, 2017
[https://www.researchgate.net/publication/316545534_MER_a_Minimal_Named-Entity_Recognition_Tagger_and_Annotation_Server]


A demo is also available at: http://labs.fc.ul.pt/mer/

## Dependencies

### awk

MER was developed and tested using the GNU awk (gawk) and grep. If you have another awk interpreter in your machine, there's no assurance that the program will work.

For example, to install GNU awk on Ubuntu:

```
sudo apt-get install gawk
```

## Basic Usage Example

### Pre-Processing of a Lexicon

Let's walk trough an example of adding a sample lexicon to MER. 

First, we have to create the lexicon file in the _data_ folder:

```txt
α-maltose
nicotinic acid
nicotinic acid D-ribonucleotide
nicotinic acid-adenine dinucleotide phosphate
```

Assuming that the file is called __lexicon.txt__, you process it as follows:

```shell
(cd data; ../produce_data_files.sh lexicon.txt)
```

Some examples of labels are shown as output so you can check that it worked.
This will create all the necessary files to use MER with the given lexicon. 

### Recognizing Entities

The script receives as input a text and a lexicon:

```shell
./get_entities.sh [text] [lexicon]
```

So, let's try to find mentions in a snippet of text:

```shell
./get_entities.sh 'α-maltose and nicotinic acid was found, but not nicotinic acid D-ribonucleotide' lexicon
```

The output will be a TSV looking like this:

```tsv
0       9       α-maltose
14	28	nicotinic acid
48	62	nicotinic acid
48	79	nicotinic acid D-ribonucleotide
```

The first column corresponds to the start-index, the second to the end-index and the third to the annotated term.

## Linking Entities

If you create a links file named __lexicon_links.tsv__ in the _data_ folder associating each label with an URI:

```txt
α-maltose                                       http://purl.obolibrary.org/obo/CHEBI_18167
nicotinic acid                                  http://purl.obolibrary.org/obo/CHEBI_15940
nicotinic acid d-ribonucleotide                 http://purl.obolibrary.org/obo/CHEBI_15763
nicotinic acid-adenine dinucleotide phosphate   http://purl.obolibrary.org/obo/CHEBI_76072
```

Then the mentions in a snippet of text will be associated to the respective identifier:

```shell
./get_entities.sh 'α-maltose and nicotinic acid was found, but not nicotinic acid D-ribonucleotide' lexicon
```

The output will be a TSV looking like this:

```tsv
0       9       α-maltose                       http://purl.obolibrary.org/obo/CHEBI_18167
14      28      nicotinic acid                  http://purl.obolibrary.org/obo/CHEBI_15940
48      62      nicotinic acid                  http://purl.obolibrary.org/obo/CHEBI_15940
48      79      nicotinic acid D-ribonucleotide http://purl.obolibrary.org/obo/CHEBI_15763
```

## Ontologies and PubMed

Now, lets recognize and map terms from an ontology in PubMed abstracts.

### DOID (Human Disease Ontology):

For example, you can start by downloading the Human Disease Ontology:

```shell 
(cd data; wget https://raw.githubusercontent.com/DiseaseOntology/HumanDiseaseOntology/master/src/ontology/doid.owl)
```

and process it:

```shell
(cd data; ../produce_data_files.sh doid.owl)
```

Now, download some abstracts from PubMed, for example ([29490421](https://www.ncbi.nlm.nih.gov/pubmed/29490421) and [29490060](https://www.ncbi.nlm.nih.gov/pubmed/29490060))

```shell
text=$(curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=29490421,29490060&retmode=text&rettype=xml" | xmllint --xpath '//AbstractText/text()' /dev/stdin)
```

Check the diseases recognized: 

```shell
./get_entities.sh "$text" doid
```

The output should be something like this:

```txt
348     354     asthma                                  http://purl.obolibrary.org/obo/DOID_2841
359     363     COPD                                    http://purl.obolibrary.org/obo/DOID_3083
496     500     COPD                                    http://purl.obolibrary.org/obo/DOID_3083
504     510     asthma                                  http://purl.obolibrary.org/obo/DOID_2841
1066    1076    bronchitis                              http://purl.obolibrary.org/obo/DOID_6132
1095    1101    asthma                                  http://purl.obolibrary.org/obo/DOID_2841
1135    1142    disease                                 http://purl.obolibrary.org/obo/DOID_4
1306    1314    impetigo                                http://purl.obolibrary.org/obo/DOID_8504
1316    1320    acne                                    http://purl.obolibrary.org/obo/DOID_6543
1322    1337    gastroenteritis                         http://purl.obolibrary.org/obo/DOID_2326
2015    2025    bronchitis                              http://purl.obolibrary.org/obo/DOID_6132
1173    1185    otitis media                            http://purl.obolibrary.org/obo/DOID_10754
2156    2168    otitis media                            http://purl.obolibrary.org/obo/DOID_10754
1105    1142    chronic obstructive pulmonary disease   http://purl.obolibrary.org/obo/DOID_3083
1281    1304    urinary tract infection                 http://purl.obolibrary.org/obo/DOID_13148
```

If you want just a list of terms:
```shell
./get_entities.sh "$text" doid | cut -f 3,4 | sort | uniq
```
you will get the following output: 

```txt
acne                                    http://purl.obolibrary.org/obo/DOID_6543
asthma                                  http://purl.obolibrary.org/obo/DOID_2841
bronchitis                              http://purl.obolibrary.org/obo/DOID_6132
chronic obstructive pulmonary disease   http://purl.obolibrary.org/obo/DOID_3083
COPD                                    http://purl.obolibrary.org/obo/DOID_3083
disease                                 http://purl.obolibrary.org/obo/DOID_4
gastroenteritis                         http://purl.obolibrary.org/obo/DOID_2326
impetigo                                http://purl.obolibrary.org/obo/DOID_8504
otitis media                            http://purl.obolibrary.org/obo/DOID_10754
urinary tract infection                 http://purl.obolibrary.org/obo/DOID_13148
```

For example, you can now use these IDs to calculate their semantic similarity using [DiShIn](https://github.com/lasigeBioTM/DiShIn)

### ChEBI (Chemical Entities of Biological Interest)
```shell 
(cd data; wget ftp://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi_lite.owl)
(cd data; ../produce_data_files.sh chebi_lite.owl)
```

```shell
./get_entities.sh 'α-maltose and nicotinic acid was found, but not nicotinic acid D-ribonucleotide' chebi_lite
```

you will get the following output: 

```txt
24	28	acid				http://purl.obolibrary.org/obo/CHEBI_37527
58	62	acid				http://purl.obolibrary.org/obo/CHEBI_37527
14	28	nicotinic acid			http://purl.obolibrary.org/obo/CHEBI_15940
48	62	nicotinic acid			http://purl.obolibrary.org/obo/CHEBI_15940
48	79	nicotinic acid D-ribonucleotide	http://purl.obolibrary.org/obo/CHEBI_15763
```

### HP (Human Phenotype Ontology)

```shell
(cd data; wget http://purl.obolibrary.org/obo/hp.owl)
(cd data; ../produce_data_files.sh hp.owl)
```
Now executing MER for the same abstracts downloaded in the steps above when using the Disease Ontology but now using Human Phenotype Ontology:

```shell
./get_entities.sh "$text" hp
```

you will get the following output: 

```txt
348     354     asthma                                  http://purl.obolibrary.org/obo/HP_0002099
359     363     COPD                                    http://purl.obolibrary.org/obo/HP_0006510
496     500     COPD                                    http://purl.obolibrary.org/obo/HP_0006510
504     510     asthma                                  http://purl.obolibrary.org/obo/HP_0002099
1059    1064    cough                                   http://purl.obolibrary.org/obo/HP_0012735
1066    1076    bronchitis                              http://purl.obolibrary.org/obo/HP_0012387
1095    1101    asthma                                  http://purl.obolibrary.org/obo/HP_0002099
1105    1112    chronic                                 http://purl.obolibrary.org/obo/HP_0011010
1316    1320    acne                                    http://purl.obolibrary.org/obo/HP_0001061
1527    1532    acute                                   http://purl.obolibrary.org/obo/HP_0011009
1918    1923    acute                                   http://purl.obolibrary.org/obo/HP_0011009
1924    1929    cough                                   http://purl.obolibrary.org/obo/HP_0012735
2015    2025    bronchitis                              http://purl.obolibrary.org/obo/HP_0012387
2150    2155    acute                                   http://purl.obolibrary.org/obo/HP_0011009
1173    1185    otitis media                            http://purl.obolibrary.org/obo/HP_0000388
2156    2168    otitis media                            http://purl.obolibrary.org/obo/HP_0000388
1105    1142    chronic obstructive pulmonary disease   http://purl.obolibrary.org/obo/HP_0006510
1193    1220    respiratory tract infection             http://purl.obolibrary.org/obo/HP_0011947
1228    1255    respiratory tract infection             http://purl.obolibrary.org/obo/HP_0011947
1281    1304    urinary tract infection                 http://purl.obolibrary.org/obo/HP_0000010
```

## Test

To check if the result is what was expected try:

```shell
./test.sh
```

if something is wrong, please check if you are using UTF-8 encoding and that you have GNU awk and grep installed. 


