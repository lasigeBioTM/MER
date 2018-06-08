# MER (Minimal Named-Entity Recognizer)

MER is a Named-Entity Recognition tool which given any lexicon and any input text returns the list of 
terms recognized in the text, including their exact location (annotations).

Given an ontology (owl file) MER is also able to link the entities to their classes.

More information about MER can be found in https://www.researchgate.net/publication/316545534_MER_a_Minimal_Named-Entity_Recognition_Tagger_and_Annotation_Server

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

Assuming that the file is called "lexicon.txt", you process it as follows:

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
./get_entities.sh 'α-maltose and nicotinic acid D-ribonucleotide was found, but not nicotinic acid' lexicon
```

The output will be a TSV looking like this:

```tsv
0       9       α-maltose
14      28      nicotinic acid
65      79      nicotinic acid
14      45      nicotinic acid D-ribonucleotide
```

The first column corresponds to the start-index, the second to the end-index and the third to the annotated term.

## Ontology and PubMed

Now, lets recognize and map terms from an ontology in PubMed abstracts.

For example, you can start by downloading the human disease ontology:

```shell 
(cd data; wget ://raw.githubusercontent.com/DiseaseOntology/HumanDiseaseOntology/master/src/ontology/deprecated/DO_Production_NON_Ontology_Files/doid-simple.owl)
```

and process it:

```shell
(cd data; ../produce_data_files.sh doid-simple.owl)
```

Now, download some abstracts from PubMed, for example ([29490421](https://www.ncbi.nlm.nih.gov/pubmed/29490421) and [29490060](https://www.ncbi.nlm.nih.gov/pubmed/29490060))

```shell
text=$(curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=29490421,29490060&retmode=text&rettype=xml" | xmllint --xpath '//AbstractText/text()' /dev/stdin)
```

Check the diseases recognized: 

```shell
./get_entities.sh "$text" doid-simple 
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
./get_entities.sh "$text" doid-simple | cut -f 3,4 | sort | uniq
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

## Test

To check if the result is what was expected try:

```shell
./test.sh
```

if something is wrong, please check if you are using UTF-8 encoding and that you have GNU awk and grep installed. 


