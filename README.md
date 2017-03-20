# MER (Minimal Named-Entity Recognizer)

Before using the program, you'll have to run 

```
bash get_data.sh
```

To run the tests do:

```
python -m unittest discover
```

## Bash Dependencies

### xmlstarlet

http://xmlstar.sourceforge.net/download.php

### awk

MER was developed and tested using the GNU awk (gawk). If you have another awk interpreter in your machine, there's no assurance that the program will work.

To install GNU awk on Ubuntu:

```
sudo apt-get install gawk
```
