FROM ubuntu:18.04

RUN apt-get update 
RUN apt-get install -y \
    gawk \
    unzip \
    bc \
    locales \
    curl 

RUN locale-gen en_US.UTF-8
#COPY ./default_locale /etc/default/locale
#RUN chmod 0755 /etc/default/locale
ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8

RUN curl -O -L https://github.com/lasigeBioTM/MER/archive/master.zip
RUN ls -l master.zip
RUN unzip master.zip
RUN mv MER-master MER
WORKDIR /MER

WORKDIR /MER/data
RUN curl -O http://labs.rd.ciencias.ulisboa.pt/mer/data/lexicons202103.tgz
RUN tar -xzf lexicons202103.tgz
WORKDIR /MER

# BEGIN get_similarity.sh requirements 

RUN apt-get install -y \
    sqlite3 \
    python

RUN curl -O http://labs.rd.ciencias.ulisboa.pt/dishin/dishin.py
RUN curl -O http://labs.rd.ciencias.ulisboa.pt/dishin/ssm.py
RUN curl -O http://labs.rd.ciencias.ulisboa.pt/dishin/annotations.py

RUN curl -O http://labs.rd.ciencias.ulisboa.pt/dishin/chebi202104.db.gz
RUN gunzip -N chebi202104.db.gz 
RUN curl -O http://labs.rd.ciencias.ulisboa.pt/dishin/go202104.db.gz
RUN gunzip -N go202104.db.gz
RUN curl -O http://labs.rd.ciencias.ulisboa.pt/dishin/hp202104.db.gz
RUN gunzip -N hp202104.db.gz
RUN curl -O http://labs.rd.ciencias.ulisboa.pt/dishin/doid202104.db.gz
RUN gunzip -N doid202104.db.gz
RUN curl -O http://labs.rd.ciencias.ulisboa.pt/dishin/mesh202104.db.gz
RUN gunzip -N mesh202104.db.gz
RUN curl -O http://labs.rd.ciencias.ulisboa.pt/dishin/radlex202104.db.gz
RUN gunzip -N radlex202104.db.gz
RUN curl -O http://labs.rd.ciencias.ulisboa.pt/dishin/wordnet202104.db.gz
RUN gunzip -N wordnet202104.db.gz

## END get_similarity.sh requirements 

RUN apt-get autoremove
RUN apt-get clean 

## To build:
## docker build -t mer-image .
## To execute:
#### docker run -it --rm --name mer-container mer-image
## Testing:
####  .test.sh
####  ./get_entities.sh "α-maltose and nicotinic acid was found, but not nicotinic acid D-ribonucleotide" lexicon | ./get_similarity.sh Lin DiShIn . chebi.db

