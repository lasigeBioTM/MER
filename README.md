[![GitHub stars](https://img.shields.io/github/stars/lasigeBioTM/MER.svg)](https://github.com/lasigeBioTM/MER/stargazers)

# MER (Minimal Named-Entity Recognizer)

MER is a Named-Entity Recognition tool that identifies terms from any lexicon within input text, providing their exact locations (annotations). 
It can also link recognized entities to their respective classes when provided with an ontology (OWL file).

A demo is available at: [MER Demo](https://labs.rd.ciencias.ulisboa.pt/mer/)

## New Stuff

### 2024
- **LEXICONS**: Package [here](https://labs.rd.ciencias.ulisboa.pt/mer/lexicons202407.tgz) is available.
- **COMMENTS**: More comments were added to the scripts to improve readability.

### 2023
- **ONTOLOGIES**: New examples added, namely the ontologies: OSCI, CL, ENVO, and ECTO.

### 2021
- **DOCKER**: Image available: [fjmc/mer-image](https://hub.docker.com/r/fjmc/mer-image).
- **MULTILINGUAL**: English, Spanish, and Portuguese lexicons using DeCS.
- **PYTHON**: Interface: [lasigeBioTM/merpy](https://github.com/lasigeBioTM/merpy/).
- **SIMILARITY**: `get_similarities.sh` finds the most similar term also recognized. See [here](https://github.com/lasigeBioTM/MER#Similarity).


## References: 
- **MER: a Shell Script and Annotation Server for Minimal Named Entity Recognition and Linking**  
  F. Couto and A. Lamurias  
  *Journal of Cheminformatics*, 10:58, 2018  
  [DOI: 10.1186/s13321-018-0312-9](https://doi.org/10.1186/s13321-018-0312-9)

- **MER: a Minimal Named-Entity Recognition Tagger and Annotation Server**  
  F. Couto, L. Campos, and A. Lamurias  
  *BioCreative V.5 Challenge Evaluation*, 2017  
  [ResearchGate](https://www.researchgate.net/publication/316545534_MER_a_Minimal_Named-Entity_Recognition_Tagger_and_Annotation_Server)

## System Requirements

### Installing GNU awk (gawk) on Ubuntu

MER was developed and tested using GNU awk (gawk) and grep. Please note that using another awk interpreter may not guarantee the program's functionality.

To install GNU awk on Ubuntu, use the following command:

```bash
sudo apt-get install gawk
```

## Basic Usage Example

### Pre-Processing of a Lexicon

Let's walk trough an example of adding a sample lexicon to MER. 

First, create the lexicon file in the `data` folder:

```txt
α-maltose
nicotinic acid
nicotinic acid D-ribonucleotide
nicotinic acid-adenine dinucleotide phosphate
```

Assuming that the file is called `lexicon.txt`, you process it as follows:

```bash
(cd data; ../produce_data_files.sh lexicon.txt)
```

After processing, examples of labels will be shown as output to verify the operation. 
This step generates all the necessary files to utilize MER with the provided lexicon.

### Recognizing Entities

The script receives as input a text and a lexicon:

```shell
./get_entities.sh [text] [lexicon]
```

Let's try to find mentions in a snippet of text:

```shell
./get_entities.sh 'α-maltose and nicotinic acid was found, but not nicotinic acid D-ribonucleotide' lexicon
```

The output will be a TSV looking like this:

```tsv
0         9         α-maltose
14        28        nicotinic acid
48        62        nicotinic acid
48        79        nicotinic acid D-ribonucleotide
```

The first column corresponds to the start-index, the second to the end-index and the third to the annotated term:

```tsv
          1         2         3         4         5         6         7         
01234567890123456789012345678901234567890123456789012345678901234567890123456789
α-maltose and nicotinic acid was found, but not nicotinic acid D-ribonucleotide
```

## Test

To check if the result is what was expected try:

```shell
./test.sh
```

if something is wrong, please check if you are using UTF-8 encoding and that you have GNU awk and grep installed. 


## Linking Entities

If you create a links file named `lexicon_links.tsv` in the `data` folder associating each label (in lower case) with an URI:
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
1578  1592  nicotinic acid  http://purl.obolibrary.org/obo/CHEBI_15940
1731  1745  nicotinic acid  http://purl.obolibrary.org/obo/CHEBI_15940
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
185   198   fertilization             http://purl.obolibrary.org/obo/GO_0009566
284   306   PPAR signaling pathway    http://purl.obolibrary.org/obo/GO_0035357
289   298   signaling                 http://purl.obolibrary.org/obo/GO_0023052
289   306   signaling pathway         http://purl.obolibrary.org/obo/GO_0007165
1157  1179  PPAR signaling pathway    http://purl.obolibrary.org/obo/GO_0035357
1162  1171  signaling                 http://purl.obolibrary.org/obo/GO_0023052
1162  1179  signaling pathway         http://purl.obolibrary.org/obo/GO_0007165
1280  1302  PPAR signaling pathway    http://purl.obolibrary.org/obo/GO_0035357
1285  1294  signaling                 http://purl.obolibrary.org/obo/GO_0023052
1285  1302  signaling pathway         http://purl.obolibrary.org/obo/GO_0007165
1303  1318  gene expression           http://purl.obolibrary.org/obo/GO_0010467
1547  1569  PPAR signaling pathway    http://purl.obolibrary.org/obo/GO_0035357
1552  1561  signaling                 http://purl.obolibrary.org/obo/GO_0023052
1552  1569  signaling pathway         http://purl.obolibrary.org/obo/GO_0007165
1641  1659  glucose metabolism        http://purl.obolibrary.org/obo/GO_0006006
1649  1659  metabolism                http://purl.obolibrary.org/obo/GO_0008152
1661  1682  inflammatory response     http://purl.obolibrary.org/obo/GO_0006954
1862  1884  PPAR signaling pathway    http://purl.obolibrary.org/obo/GO_0035357
1867  1876  signaling                 http://purl.obolibrary.org/obo/GO_0023052
1867  1884  signaling pathway         http://purl.obolibrary.org/obo/GO_0007165
1989  2001  pathogenesis              http://purl.obolibrary.org/obo/GO_0001897
```

### Chemical Entities of Biological Interest (ChEBI) 

Download the ontology:
```shell 
(cd data; curl -L -O  http://purl.obolibrary.org/obo/chebi/chebi_lite.owl)
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
0     8     Electron                  http://purl.obolibrary.org/obo/CHEBI_10545
160   165   ester                     http://purl.obolibrary.org/obo/CHEBI_35701
213   218   ester                     http://purl.obolibrary.org/obo/CHEBI_35701
285   290   ester                     http://purl.obolibrary.org/obo/CHEBI_35701
342   347   ester                     http://purl.obolibrary.org/obo/CHEBI_35701
397   402   ester                     http://purl.obolibrary.org/obo/CHEBI_35701
475   480   ester                     http://purl.obolibrary.org/obo/CHEBI_35701
1051  1055  atom                      http://purl.obolibrary.org/obo/CHEBI_33250
1065  1080  isopropyl ester           http://purl.obolibrary.org/obo/CHEBI_35725
1075  1080  ester                     http://purl.obolibrary.org/obo/CHEBI_35701
1128  1132  acid                      http://purl.obolibrary.org/obo/CHEBI_37527
1145  1152  propene                   http://purl.obolibrary.org/obo/CHEBI_16052
1206  1211  ester                     http://purl.obolibrary.org/obo/CHEBI_35701
1261  1265  acid                      http://purl.obolibrary.org/obo/CHEBI_37527
1289  1296  radical                   http://purl.obolibrary.org/obo/CHEBI_26519
1348  1354  methyl                    http://purl.obolibrary.org/obo/CHEBI_29309
1544  1550  methyl                    http://purl.obolibrary.org/obo/CHEBI_29309
1621  1627  proton                    http://purl.obolibrary.org/obo/CHEBI_24636
1707  1719  benzoic acid              http://purl.obolibrary.org/obo/CHEBI_30746
1715  1719  acid                      http://purl.obolibrary.org/obo/CHEBI_37527
1789  1803  nicotinic acid            http://purl.obolibrary.org/obo/CHEBI_15940
1799  1803  acid                      http://purl.obolibrary.org/obo/CHEBI_37527
1844  1858  carbonyl group            http://purl.obolibrary.org/obo/CHEBI_23019
1853  1858  group                     http://purl.obolibrary.org/obo/CHEBI_24433
1929  1941  benzoic acid              http://purl.obolibrary.org/obo/CHEBI_30746
1937  1941  acid                      http://purl.obolibrary.org/obo/CHEBI_37527
1984  1998  nicotinic acid            http://purl.obolibrary.org/obo/CHEBI_15940
1994  1998  acid                      http://purl.obolibrary.org/obo/CHEBI_37527
2094  2097  ion                       http://purl.obolibrary.org/obo/CHEBI_24870
2190  2193  ion                       http://purl.obolibrary.org/obo/CHEBI_24870
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
50    53    dry                       http://purl.obolibrary.org/obo/PATO_0001801
348   354   asthma                    http://purl.obolibrary.org/obo/HP_0002099
359   363   COPD                      http://purl.obolibrary.org/obo/HP_0006510
496   500   COPD                      http://purl.obolibrary.org/obo/HP_0006510
504   510   asthma                    http://purl.obolibrary.org/obo/HP_0002099
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
348   354   asthma                    http://purl.obolibrary.org/obo/DOID_2841
359   363   COPD                      http://purl.obolibrary.org/obo/DOID_3083
496   500   COPD                      http://purl.obolibrary.org/obo/DOID_3083
504   510   asthma                    http://purl.obolibrary.org/obo/DOID_2841
```


### Ontology for Stem Cell Investigations (OSCI) Example 

Download the ontology:
```shell 
(cd data; curl -L -O https://raw.githubusercontent.com/stemcellontologyresource/OSCI/master/src/ontology/osci.owl)
```

Process it:
```shell
(cd data; ../produce_data_files.sh osci.owl)
```

Download an abstract from PubMed, for example [30053745](https://www.ncbi.nlm.nih.gov/pubmed/30053745):
```shell
text=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=30053745&retmode=text&rettype=xml" | xmllint --xpath '//AbstractText/text()' /dev/stdin)
```

Recognize the entities in the abstract: 
```shell
./get_entities.sh "$text" osci
```

The output should be something like this:
```txt
325   329   cell                      http://purl.obolibrary.org/obo/CL_0000000
447   452   human                     http://purl.obolibrary.org/obo/NCBITaxon_9606
475   480   human                     http://purl.obolibrary.org/obo/NCBITaxon_9606
531   536   human                     http://purl.obolibrary.org/obo/NCBITaxon_9606
545   556   pluripotent               http://purl.obolibrary.org/obo/PATO_0001403
601   610   Stem cell                 http://purl.obolibrary.org/obo/CL_0000034
606   610   cell                      http://purl.obolibrary.org/obo/CL_0000000
691   702   pluripotent               http://purl.obolibrary.org/obo/PATO_0001403
743   748   human                     http://purl.obolibrary.org/obo/NCBITaxon_9606
749   755   neuron                    http://purl.obolibrary.org/obo/CL_0000540
798   804   neuron                    http://purl.obolibrary.org/obo/CL_0000540
913   929   Neural stem cell          http://purl.obolibrary.org/obo/CL_0000047
920   929   stem cell                 http://purl.obolibrary.org/obo/CL_0000034
925   929   cell                      http://purl.obolibrary.org/obo/CL_0000000
975   984   stem cell                 http://purl.obolibrary.org/obo/CL_0000034
980   984   cell                      http://purl.obolibrary.org/obo/CL_0000000
```

### Cell Ontology (CL) Example 

Download the ontology:
```shell 
(cd data; curl -L -O http://purl.obolibrary.org/obo/cl.owl)
```

Process it:
```shell
(cd data; ../produce_data_files.sh cl.owl)
```

Download an abstract from PubMed, for example [30053745](https://www.ncbi.nlm.nih.gov/pubmed/30053745):
```shell
text=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=30053745&retmode=text&rettype=xml" | xmllint --xpath '//AbstractText/text()' /dev/stdin)
```

Recognize the entities in the abstract: 
```shell
./get_entities.sh "$text" cl
```

The output should be something like this:
```txt
255   268   dentate gyrus             http://purl.obolibrary.org/obo/UBERON_0001885
263   268   gyrus                     http://purl.obolibrary.org/obo/UBERON_0000200
276   287   hippocampus               http://purl.obolibrary.org/obo/UBERON_0001954
315   329   ependymal cell            http://purl.obolibrary.org/obo/CL_0000065
325   329   cell                      http://purl.obolibrary.org/obo/CL_0000000
447   452   human                     http://purl.obolibrary.org/obo/NCBITaxon_9606
475   480   human                     http://purl.obolibrary.org/obo/NCBITaxon_9606
531   536   human                     http://purl.obolibrary.org/obo/NCBITaxon_9606
601   610   Stem cell                 http://purl.obolibrary.org/obo/CL_0000034
606   610   cell                      http://purl.obolibrary.org/obo/CL_0000000
743   748   human                     http://purl.obolibrary.org/obo/NCBITaxon_9606
749   755   neuron                    http://purl.obolibrary.org/obo/CL_0000540
798   804   neuron                    http://purl.obolibrary.org/obo/CL_0000540
913   929   Neural stem cell          http://purl.obolibrary.org/obo/CL_0000047
920   929   stem cell                 http://purl.obolibrary.org/obo/CL_0000034
925   929   cell                      http://purl.obolibrary.org/obo/CL_0000000
975   984   stem cell                 http://purl.obolibrary.org/obo/CL_0000034
980   984   cell                      http://purl.obolibrary.org/obo/CL_0000000
1041  1046  great                     http://purl.obolibrary.org/obo/PATO_0000586
```

### Environmental conditions, treatments and exposures ontology (ECTO) Example 

Download the ontology:
```shell 
(cd data; curl -L -O http://purl.obolibrary.org/obo/ecto.owl)
```

Process it:
```shell
(cd data; ../produce_data_files.sh ecto.owl)
```

Download an abstract from PubMed, for example [34303912](https://www.ncbi.nlm.nih.gov/pubmed/34303912):
```shell
text=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=34303912&retmode=text&rettype=xml" | xmllint --xpath '//AbstractText/text()' /dev/stdin)
```

Recognize the entities in the abstract: 
```shell
./get_entities.sh "$text" ecto
```

The output should be something like this:
```txt
0     5     Water                     http://purl.obolibrary.org/obo/CHEBI_15377
30    35    human                     http://purl.obolibrary.org/obo/NCBITaxon_9606
139   150   environment               http://purl.obolibrary.org/obo/ENVO_01000254
177   182   water                     http://purl.obolibrary.org/obo/CHEBI_15377
200   206   planet                    http://purl.obolibrary.org/obo/ENVO_01000800
237   242   water                     http://purl.obolibrary.org/obo/CHEBI_15377
237   252   water pollution           http://purl.obolibrary.org/obo/ENVO_02500039
243   252   pollution                 http://purl.obolibrary.org/obo/ENVO_02500036
339   350   environment               http://purl.obolibrary.org/obo/ENVO_01000254
397   404   process                   http://purl.obolibrary.org/obo/BFO_0000015
449   462   concentration             http://purl.obolibrary.org/obo/PATO_0000033
542   553   agriculture               http://purl.obolibrary.org/obo/ENVO_01001246
585   591   energy                    http://purl.obolibrary.org/obo/ENVO_2000015
661   665   role                      http://purl.obolibrary.org/obo/BFO_0000023
764   771   quality                   http://purl.obolibrary.org/obo/BFO_0000019
811   821   technology                http://purl.obolibrary.org/obo/NCIT_C17187
1101  1110  behaviour                 http://purl.obolibrary.org/obo/GO_0007610
1167  1177  technology                http://purl.obolibrary.org/obo/NCIT_C17187
1192  1198  energy                    http://purl.obolibrary.org/obo/ENVO_2000015
1412  1422  technology                http://purl.obolibrary.org/obo/NCIT_C17187
```

### Environment Ontology (ENVO) Example 

Download the ontology:
```shell 
(cd data; curl -L -O http://purl.obolibrary.org/obo/envo.owl)
```

Process it:
```shell
(cd data; ../produce_data_files.sh envo.owl)
```

Download an abstract from PubMed, for example [34303912](https://www.ncbi.nlm.nih.gov/pubmed/34303912):
```shell
text=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=34303912&retmode=text&rettype=xml" | xmllint --xpath '//AbstractText/text()' /dev/stdin)
```

Recognize the entities in the abstract: 
```shell
./get_entities.sh "$text" envo
```

The output should be something like this:
```txt
0     5     Water                     http://purl.obolibrary.org/obo/CHEBI_15377
30    35    human                     http://purl.obolibrary.org/obo/NCBITaxon_9606
139   150   environment               http://purl.obolibrary.org/obo/ENVO_01000254
177   182   water                     http://purl.obolibrary.org/obo/CHEBI_15377
200   206   planet                    http://purl.obolibrary.org/obo/ENVO_01000800
237   242   water                     http://purl.obolibrary.org/obo/CHEBI_15377
237   252   water pollution           http://purl.obolibrary.org/obo/ENVO_02500039
243   252   pollution                 http://purl.obolibrary.org/obo/ENVO_02500036
339   350   environment               http://purl.obolibrary.org/obo/ENVO_01000254
397   404   process                   http://purl.obolibrary.org/obo/BFO_0000015
449   462   concentration             http://purl.obolibrary.org/obo/PATO_0000033
542   553   agriculture               http://purl.obolibrary.org/obo/ENVO_01001246
585   591   energy                    http://purl.obolibrary.org/obo/ENVO_2000015
661   665   role                      http://purl.obolibrary.org/obo/BFO_0000023
764   771   quality                   http://purl.obolibrary.org/obo/BFO_0000019
1192  1198  energy                    http://purl.obolibrary.org/obo/ENVO_2000015
```

<!--
### Radiology Lexicon (RadLex) Example

Find the link to the RDF/XML version from http://bioportal.bioontology.org/ontologies/RADLEX

Download it as radlex.rdf:
```shell
(cd data; curl -L -o radlex.rdf https://data.bioontology.org/ontologies/RADLEX/download?apikey=...&download_format=rdf)
```

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
337   344   therapy                   http://radlex.org/RID/RID8
348   354   asthma                    http://radlex.org/RID/RID5327
359   363   COPD                      http://radlex.org/RID/RID5317
468   475   therapy                   http://radlex.org/RID/RID8
496   500   COPD                      http://radlex.org/RID/RID5317
504   510   asthma                    http://radlex.org/RID/RID5327
511   518   patient                   http://radlex.org/RID/RID49815
587   594   patient                   http://radlex.org/RID/RID49815
```
-->

### DeCS Multilingual Example

Request the XML files of DeCS in Portuguese, Spanish and English from https://decs.bvsalud.org/

Process it:
```shell
(cd data; ../produce_data_files.sh bireme_decs_eng2020.xml)
(cd data; ../produce_data_files.sh bireme_decs_spa2020.xml)
(cd data; ../produce_data_files.sh bireme_decs_por2020.xml)
```

Download a multilingual corpus, e.g. from https://sites.google.com/view/felipe-soares/datasets
Text from https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4458994
```shell
text_eng='This situation also contributes to respiratory aspiration and aspiration pneumonia, which is evidenced by a persistent cough with sputum or by other signs such as fever, tachypnea, or focal consolidation confirmed by radiographic imaging'
text_spa='Esa situación también contribuye para la aspiración respiratoria y para la neumonía espirativa, que puede ser evidenciada por tos persistente con expectoración o por otras señales como fiebre, taquipnea, consolidación focal, siendo confirmada por la imagen radiográfica'
text_por='Essa situação também contribui para a aspiração respiratória e para a pneumonia aspirativa, que pode ser evidenciada por tosse persistente com expectoração ou por outros sinais como: febre, taquipneia, consolidação focal, sendo confirmada pela imagem radiográfica'
```

Recognize the entities in the abstract: 
```shell
./get_entities.sh "$text_eng" bireme_decs_eng2020
./get_entities.sh "$text_spa" bireme_decs_spa2020
./get_entities.sh "$text_por" bireme_decs_por2020
```

The output should be something like this:
```txt
35    57    respiratory aspiration    https://decs.bvsalud.org/ths/?filter=ths_regid&q=D053120
73    82    pneumonia                 https://decs.bvsalud.org/ths/?filter=ths_regid&q=D011014
119   124   cough                     https://decs.bvsalud.org/ths/?filter=ths_regid&q=D003371
130   136   sputum                    https://decs.bvsalud.org/ths/?filter=ths_regid&q=D013183
163   168   fever                     https://decs.bvsalud.org/ths/?filter=ths_regid&q=D005334
170   179   tachypnea                 https://decs.bvsalud.org/ths/?filter=ths_regid&q=D059246

41    64    aspiración respiratoria   https://decs.bvsalud.org/ths/?filter=ths_regid&q=D053120
75    83    neumonía                  https://decs.bvsalud.org/ths/?filter=ths_regid&q=D011014
126   129   tos                       https://decs.bvsalud.org/ths/?filter=ths_regid&q=D003371
185   191   fiebre                    https://decs.bvsalud.org/ths/?filter=ths_regid&q=D005334
193   202   taquipnea                 https://decs.bvsalud.org/ths/?filter=ths_regid&q=D059246

38    60    aspiração respiratória    https://decs.bvsalud.org/ths/?filter=ths_regid&q=D053120
70    79    pneumonia                 https://decs.bvsalud.org/ths/?filter=ths_regid&q=D011014
70    90    pneumonia aspirativa      https://decs.bvsalud.org/ths/?filter=ths_regid&q=D011015
121   126   tosse                     https://decs.bvsalud.org/ths/?filter=ths_regid&q=D003371
183   188   febre                     https://decs.bvsalud.org/ths/?filter=ths_regid&q=D005334
190   200   taquipneia                https://decs.bvsalud.org/ths/?filter=ths_regid&q=D059246
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
4     11    article
50    53    dry
54    60    powder
91    95    data
105   115   literature
192   196   well
288   291   may
292   301   influence
306   314   efficacy
319   325   safety
329   336   inhaler
337   344   therapy
348   354   asthma
381   384   use
396   404   addition
423   432   potential
448   456   efficacy
460   467   inhaler
468   475   therapy
485   491   doctor
504   510   asthma
511   518   patient
519   530   perspective
556   562   choice
563   572   algorithm
587   594   patient
```

##  Processed Lexicons
```shell
cd data
curl -L -O https://labs.rd.ciencias.ulisboa.pt/mer/data/lexicons202407.tgz
tar -xzf lexicons202407.tgz
cd ..
```

##  BioCreative V.5 Challenge Evaluation (BeCalm) Lexicons

```shell
cd data
curl -L -O https://labs.rd.ciencias.ulisboa.pt/mer/data/becalm2017.tgz
tar -xzf data2017.tgz
tar -tzf data2017.tgz | xargs -l ../produce_data_files.sh
cd ..
./get_entities.sh 'heart' tissue_and_organ
./get_entities.sh 'histoglobin' protein
./get_entities.sh 'ame-miR-2b' mirna
```

## Similarity

First install DiShIn: https://github.com/lasigeBioTM/DiShIn
Or a minimalist version:  
```shell
curl -L -O https://labs.rd.ciencias.ulisboa.pt/dishin/dishin.py
curl -L -O https://labs.rd.ciencias.ulisboa.pt/dishin/ssm.py
curl -L -O https://labs.rd.ciencias.ulisboa.pt/dishin/annotations.py
```

Before executing the _get_similarity_ script you need to select the following parameters:
- Measure: Resnik, Lin or JC
- Type: MICA or DiShIn
- Path: DiShIn installation folder
- Database: DiShIn db file with the ontology, e.g. chebi.db, go.db, hp.db, doid.db, radlex.db, or wordnet.db  

For example, download the database for ChEBI:
```shell
curl -L -O https://labs.rd.ciencias.ulisboa.pt/dishin/chebi202302.db.gz
gunzip -N chebi202302.db.gz
```

Then, just execute the _get_similarity_ script using the output of the _get_entities_ script
```shell
./get_entities.sh "α-maltose and nicotinic acid was found, but not nicotinic acid D-ribonucleotide" lexicon | ./get_similarity.sh Lin DiShIn . chebi.db
```

The output now includes for each match the most similar term and its similarity:

```txt
0       9       α-maltose                       http://purl.obolibrary.org/obo/CHEBI_18167      CHEBI_15763     0.0264373654324
14      28      nicotinic acid                  http://purl.obolibrary.org/obo/CHEBI_15940      CHEBI_15763     0.0796995701424
48      62      nicotinic acid                  http://purl.obolibrary.org/obo/CHEBI_15940      CHEBI_15763     0.0796995701424
48      79      nicotinic acid D-ribonucleotide http://purl.obolibrary.org/obo/CHEBI_15763      CHEBI_15940     0.0796995701424
```

A multilingual example:
```shell
curl -L -O https://labs.rd.ciencias.ulisboa.pt/dishin/mesh202302.db.gz
gunzip -N mesh202302.db.gz
curl -L -O https://labs.rd.ciencias.ulisboa.pt/mer/data/lexicons202407.tgz
(cd data; tar -xzf ../lexicons202407.tgz --wildcards bireme_decs_por2024*)
./get_entities.sh "febre, tontura, pneumonia e tosse" bireme_decs_por2024 | ./get_similarity.sh Lin DiShIn . mesh.db
```

The output:
```txt
0       5       febre           https://decs.bvsalud.org/ths/?filter=ths_regid&q=D005334        D004244 0.29193507456
7       14      tontura         https://decs.bvsalud.org/ths/?filter=ths_regid&q=D004244        D005334 0.29193507456
16      25      pneumonia       https://decs.bvsalud.org/ths/?filter=ths_regid&q=D011014        D003371 0.431131076105
28      33      tosse           https://decs.bvsalud.org/ths/?filter=ths_regid&q=D003371        D011014 0.431131076105
```

As expected, fever (fever) is closer to dizziness (tontura),
and pneumonia is closer to cough (tosse).


