[![GitHub stars](https://img.shields.io/github/stars/lasigeBioTM/MER.svg)](https://github.com/lasigeBioTM/MER/stargazers)

# MER (Minimal Named-Entity Recognizer)

MER is a Named-Entity Recognition tool which given any lexicon and any input text returns the list of 
terms recognized in the text, including their exact location (annotations).

Given an ontology (owl file) MER is also able to link the entities to their classes.

A demo is also available at: http://labs.fc.ul.pt/mer/

** **NEW** **
- Python interface: https://github.com/lasigeBioTM/merpy/
- get_similarities.sh finds the most similar term also recognized (see https://github.com/lasigeBioTM/MER#Similarity)

## References: 
- MER: a Shell Script and Annotation Server for Minimal Named Entity Recognition and Linking, F. Couto and A. Lamurias, Journal of Cheminformatics, 10:58, 2018
[https://doi.org/10.1186/s13321-018-0312-9]
- MER: a Minimal Named-Entity Recognition Tagger and Annotation Server, F. Couto, L. Campos, and A. Lamurias, in BioCreative V.5 Challenge Evaluation, 2017
[https://www.researchgate.net/publication/316545534_MER_a_Minimal_Named-Entity_Recognition_Tagger_and_Annotation_Server]

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

## Test

To check if the result is what was expected try:

```shell
./test.sh
```

if something is wrong, please check if you are using UTF-8 encoding and that you have GNU awk and grep installed. 


## Linking Entities

If you create a links file named __lexicon_links.tsv__ in the _data_ folder associating each label (in lower case) with an URI:
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

## PubMed
Download an abstract from PubMed, for example [31319702](https://www.ncbi.nlm.nih.gov/pubmed/31319702):

```shell
text=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=31319702&retmode=text&rettype=xml" | xmllint --xpath '//AbstractText/text()' /dev/stdin)
```
You can add more abstracts by adding more PubMed ids separated by comma.

Recognize the entities in the abstract: 
```shell
./get_entities.sh "$text" lexicon
```

The output should be something like this:
```txt
1789      1803      nicotinic acid      http://purl.obolibrary.org/obo/CHEBI_15940
1984      1998      nicotinic acid      http://purl.obolibrary.org/obo/CHEBI_15940
```

## Ontologies

### Gene Ontology (GO) Example

Download the ontology:
```shell 
(cd data; curl -L -O http://purl.obolibrary.org/obo/go.owl)
```

Process it:
```shell
(cd data; ../produce_data_files.sh go.owl)
```

Now, download an abstract from PubMed, for example [31351426](https://www.ncbi.nlm.nih.gov/pubmed/31351426):
```shell
text=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=31351426&retmode=text&rettype=xml" | xmllint --xpath '//AbstractText/text()' /dev/stdin)
```

Recognize the entities in the abstract: 
```shell
./get_entities.sh "$text" go
```

The output should be something like this:
```txt
185            198            fertilization  http://purl.obolibrary.org/obo/GO_0009566 
289            298            signaling      http://purl.obolibrary.org/obo/GO_0023052 
1162           1171           signaling      http://purl.obolibrary.org/obo/GO_0023052 
1285           1294           signaling      http://purl.obolibrary.org/obo/GO_0023052 
1552           1561           signaling      http://purl.obolibrary.org/obo/GO_0023052 
1867           1876           signaling      http://purl.obolibrary.org/obo/GO_0023052 
1989           2001           pathogenesis   http://purl.obolibrary.org/obo/GO_0009405 
289            306            signaling pathway             http://purl.obolibrary.org/obo/GO_0007165 
1162           1179           signaling pathway             http://purl.obolibrary.org/obo/GO_0007165 
1285           1302           signaling pathway             http://purl.obolibrary.org/obo/GO_0007165 
1303           1318           gene expression               http://purl.obolibrary.org/obo/GO_0010467 
1552           1569           signaling pathway             http://purl.obolibrary.org/obo/GO_0007165 
1661           1682           inflammatory response         http://purl.obolibrary.org/obo/GO_0006954 
1867           1884           signaling pathway             http://purl.obolibrary.org/obo/GO_0007165 
284            306            PPAR signaling pathway        http://purl.obolibrary.org/obo/GO_0035357 
1157           1179           PPAR signaling pathway        http://purl.obolibrary.org/obo/GO_0035357 
1280           1302           PPAR signaling pathway        http://purl.obolibrary.org/obo/GO_0035357 
1547           1569           PPAR signaling pathway        http://purl.obolibrary.org/obo/GO_0035357 
1862           1884           PPAR signaling pathway        http://purl.obolibrary.org/obo/GO_0035357 
```

### Chemical Entities of Biological Interest (ChEBI) 

Download the ontology:
```shell 
(cd data; curl -L -O ftp://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi_lite.owl)
```

Process it:
```shell
(cd data; ../produce_data_files.sh chebi_lite.owl)
```

Download an abstract from PubMed, for example [31319702](https://www.ncbi.nlm.nih.gov/pubmed/31319702):
```shell
text=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=31319702&retmode=text&rettype=xml" | xmllint --xpath '//AbstractText/text()' /dev/stdin)
```

Recognize the entities in the abstract: 
```shell
./get_entities.sh "$text" chebi_lite
```

The output should be something like this:
```txt
0         8         Electron  http://purl.obolibrary.org/obo/CHEBI_10545 
160       165       ester     http://purl.obolibrary.org/obo/CHEBI_35701 
213       218       ester     http://purl.obolibrary.org/obo/CHEBI_35701 
285       290       ester     http://purl.obolibrary.org/obo/CHEBI_35701 
342       347       ester     http://purl.obolibrary.org/obo/CHEBI_35701 
397       402       ester     http://purl.obolibrary.org/obo/CHEBI_35701 
475       480       ester     http://purl.obolibrary.org/obo/CHEBI_35701 
1051      1055      atom      http://purl.obolibrary.org/obo/CHEBI_33250 
1075      1080      ester     http://purl.obolibrary.org/obo/CHEBI_35701 
1128      1132      acid      http://purl.obolibrary.org/obo/CHEBI_37527 
1206      1211      ester     http://purl.obolibrary.org/obo/CHEBI_35701 
1261      1265      acid      http://purl.obolibrary.org/obo/CHEBI_37527 
1348      1354      methyl    http://purl.obolibrary.org/obo/CHEBI_29309 
1544      1550      methyl    http://purl.obolibrary.org/obo/CHEBI_29309 
1621      1627      proton    http://purl.obolibrary.org/obo/CHEBI_24636 
1715      1719      acid      http://purl.obolibrary.org/obo/CHEBI_37527 
1799      1803      acid      http://purl.obolibrary.org/obo/CHEBI_37527 
1937      1941      acid      http://purl.obolibrary.org/obo/CHEBI_37527 
1994      1998      acid      http://purl.obolibrary.org/obo/CHEBI_37527 
2094      2097      ion       http://purl.obolibrary.org/obo/CHEBI_24870 
2190      2193      ion       http://purl.obolibrary.org/obo/CHEBI_24870 
1065      1080      isopropyl ester     http://purl.obolibrary.org/obo/CHEBI_35725 
1707      1719      benzoic acid        http://purl.obolibrary.org/obo/CHEBI_30746 
1789      1803      nicotinic acid      http://purl.obolibrary.org/obo/CHEBI_15940 
1929      1941      benzoic acid        http://purl.obolibrary.org/obo/CHEBI_30746 
1984      1998      nicotinic acid      http://purl.obolibrary.org/obo/CHEBI_15940
```

### Human Phenotype (HP) Example

Download the ontology:
```shell 
(cd data; curl -L -O http://purl.obolibrary.org/obo/hp.owl)
```

Process it:
```shell
(cd data; ../produce_data_files.sh hp.owl)
```

Download an abstract from PubMed, for example [29490421](https://www.ncbi.nlm.nih.gov/pubmed/29490421):
```shell
text=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=29490421&retmode=text&rettype=xml" | xmllint --xpath '//AbstractText/text()' /dev/stdin)
```

Recognize the entities in the abstract: 
```shell
./get_entities.sh "$text" hp
```

The output should be something like this:
```txt
50        53        dry       http://purl.obolibrary.org/obo/PATO_0001801 
348       354       asthma    http://purl.obolibrary.org/obo/HP_0002099 
359       363       COPD      http://purl.obolibrary.org/obo/HP_0006510 
496       500       COPD      http://purl.obolibrary.org/obo/HP_0006510 
504       510       asthma    http://purl.obolibrary.org/obo/HP_0002099
```

### Human Disease Ontology (HDO) Example 

Download the ontology:
```shell 
(cd data; curl -L -O http://purl.obolibrary.org/obo/doid.owl)
```

Process it:
```shell
(cd data; ../produce_data_files.sh doid.owl)
```

Download an abstract from PubMed, for example [29490421](https://www.ncbi.nlm.nih.gov/pubmed/29490421):
```shell
text=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=29490421&retmode=text&rettype=xml" | xmllint --xpath '//AbstractText/text()' /dev/stdin)
```

Recognize the entities in the abstract: 
```shell
./get_entities.sh "$text" doid
```

The output should be something like this:
```txt
348       354       asthma    http://purl.obolibrary.org/obo/DOID_2841 
359       363       COPD      http://purl.obolibrary.org/obo/DOID_3083 
496       500       COPD      http://purl.obolibrary.org/obo/DOID_3083 
504       510       asthma    http://purl.obolibrary.org/obo/DOID_2841
```

### Radiology Lexicon (RadLex) Example

Download the RDF/XML version from http://bioportal.bioontology.org/ontologies/RADLEX and save it as radlex.rdf

Process it:
```shell
(cd data; ../produce_data_files.sh radlex.rdf)
```

Download an abstract from PubMed, for example [29490421](https://www.ncbi.nlm.nih.gov/pubmed/29490421):
```shell
text=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=29490421&retmode=text&rettype=xml" | xmllint --xpath '//AbstractText/text()' /dev/stdin)
```

Recognize the entities in the abstract: 
```shell
./get_entities.sh "$text" radlex
```

The output should be something like this:
```txt
348       354       asthma    http://radlex.org/RID/RID5327 
504       510       asthma    http://radlex.org/RID/RID5327 
511       518       patient   http://radlex.org/RID/RID49815 
587       594       patient   http://radlex.org/RID/RID49815 
```


### WordNet Example

Download the ontology:
```shell 
(cd data; curl -L -O http://www.w3.org/2006/03/wn/wn20/rdf/wordnet-hyponym.rdf)
```

Process it:
```shell
(cd data; ../produce_data_files.sh wordnet-hyponym.rdf)
```

Download an abstract from PubMed, for example [29490421](https://www.ncbi.nlm.nih.gov/pubmed/29490421):
```shell
text=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=29490421&retmode=text&rettype=xml" | xmllint --xpath '//AbstractText/text()' /dev/stdin)
```

Recognize the entities in the abstract: 
```shell
./get_entities.sh "$text" wordnet-hyponym
```

The output should be something like this:
```txt
4       11      article 
50      53      dry     
54      60      powder  
91      95      data    
192     196     well    
288     291     may     
292     301     influence       
306     314     efficacy        
319     325     safety  
329     336     inhaler 
337     344     therapy 
348     354     asthma  
381     384     use     
423     432     potential       
448     456     efficacy        
460     467     inhaler 
468     475     therapy 
485     491     doctor  
504     510     asthma  
511     518     patient 
556     562     choice  
563     572     algorithm       
587     594     patient
```

## Similarity

First install DiShIn: https://github.com/lasigeBioTM/DiShIn 

Before executing the _get_similarity_ script you need to select the following parameters:
- Measure: Resnik, Lin or JC
- Type: MICA or DiShIn
- Path: DiShIn installation folder
- Database: DiShIn db file with the ontology, e.g. chebi.db, go.db, hp.db, doid.db, radlex.db, or wordnet.db  

Then, just execute the _get_similarity_ script using the output of the _get_entities_ script
```shell
./get_entities.sh "α-maltose and nicotinic acid was found, but not nicotinic acid D-ribonucleotide" lexicon | ./get_similarity.sh Lin DiShIn ../DiShIn chebi.db
```

The output now includes for each match the most similar term and its similarity:

```txt
0    9    α-maltose                          http://purl.obolibrary.org/obo/CHEBI_18167   CHEBI_15940    0.025986492828
14   28   nicotinic acid                     http://purl.obolibrary.org/obo/CHEBI_15940   CHEBI_15763    0.0690850358636
48   62   nicotinic acid                     http://purl.obolibrary.org/obo/CHEBI_15940   CHEBI_15763    0.0690850358636
48   79   nicotinic acid D-ribonucleotide    http://purl.obolibrary.org/obo/CHEBI_15763   CHEBI_15940    0.0690850358636
```

##  Processed Lexicons
```shell
cd data
curl -L -O http://labs.rd.ciencias.ulisboa.pt/mer/data/lexicons202005.tgz
tar -xzf lexicons202005.tgz
cd ..
```

##  BioCreative V.5 Challenge Evaluation (BeCalm) Lexicons

```shell
cd data
curl -L -O http://labs.rd.ciencias.ulisboa.pt/mer/data/becalm2017.tgz
tar -xzf data2017.tgz
tar -tzf data2017.tgz | xargs -l ../produce_data_files.sh
cd ..
./get_entities.sh 'heart' tissue_and_organ
./get_entities.sh 'histoglobin' protein
./get_entities.sh 'ame-miR-2b' mirna
```

