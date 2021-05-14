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

WORKDIR /MER

RUN apt-get autoremove
RUN apt-get clean 

## To build:
## docker build -t mer-image .
## To execute:
#### docker run -it --rm --name mer-container mer-image
## Testing:
####  .test.sh
####  ./get_entities.sh "α-maltose and nicotinic acid was found, but not nicotinic acid D-ribonucleotide" lexicon | ./get_similarity.sh Lin DiShIn . chebi.db

