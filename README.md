# IBELight

IBELight is a gazeeter-based Named-Entity Recognition system which annotates in the text terms present in an arbitrary gazeeter provided by the user. IBELight is better described in [link to proceedings paper]. 

## Preparation of Gazeeters 

Let's walk trough an example of adding a primates-related gazeeter to IBELight. 

First, I have to create my gazeeter. 

```txt
Gorilla 
Human
Chimpazee 
Bonobo
```

Ok, that's enough primates for today. We save this in a file called "primates.txt" and save it in the data/ folder of IBELight. Next, we do 

```shell
cd data
bash ../produce_data_files.sh primates.txt
```

This will create all the necessary files to use IBELight with this gazeeter. 

## Usage

```shell
bash get_entities.sh [text] [gazeeter]
```

Ok, let's try to find mentions of primates in a snipper of text (be sure to be back to the IBELight home folder):

```shell
bash get_entities.sh "The gorilla punched the human in the nose" primates
```

(ouch, poor human)

The output will be a TSV looking like this:

```tsv
4  11  gorilla
24 29  human
```

The first column corresponds to the start-index, the second to the end-index and the third to the annotated term.

## Tests

To run the tests do:

```shell
python -m unittest discover
```

Tested with Python 2.7.12.
