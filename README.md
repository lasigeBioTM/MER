# MER (Minimal Named-Entity Recognizer)

MER is a lexicon-based Named-Entity Recognition system which annotates in the text terms present in an arbitrary lexicon provided by the user. MER is better described in [link to proceedings paper]. 

## Dependencies

### Operative System

This was tested and works as expected on Ubuntu 16.04 and CentOS 6. 

You can also run it on Windows using Cygwin or Git Bash, but there are some issues regarding UTF-8 characters. 

### awk

MER was developed and tested using the GNU awk (gawk). If you have another awk interpreter in your machine, there's no assurance that the program will work.

To install GNU awk on Ubuntu:

```
sudo apt-get install gawk
```

## Preparation of Lexicons 

Let's walk trough an example of adding a primates-related lexicon to MER. 

First, I have to create my lexicon. 

```txt
Gorilla 
Human
Chimpazee 
Bonobo
```

Ok, that's enough primates for today. We save this in a file called "primates.txt" and save it in the data/ folder of MER. Next, we do 

```shell
cd data
bash ../produce_data_files.sh primates.txt
```

This will create all the necessary files to use MER with this lexicon. 

## Usage

```shell
bash get_entities.sh [text] [lexicon]
```

Ok, let's try to find mentions of primates in a snipper of text (be sure to be back to the MER home folder):

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
