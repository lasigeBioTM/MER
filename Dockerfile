#### To build:
## docker build github.com/lasigeBioTM/MER -t fjmc/mer-image
#### To test it:
## docker run -it --rm --name mer-container fjmc/mer-image ./test.sh

#### To build with lexicons:
## curl -O -L https://github.com/lasigeBioTM/MER/archive/master.zip
## unzip master.zip
## cd MER-master 
## cat Dockerfile-LexiconsSimilarity >> Dockerfile
## docker build . -t fjmc/mer-image:lexicons202103
#### To test it:
## docker run -it --rm --name mer-container fjmc/mer-image:lexicons202103 /bin/bash -c './get_entities.sh "α-maltose and nicotinic acid was found, but not nicotinic acid D-ribonucleotide" lexicon | ./get_similarity.sh Lin DiShIn . chebi.db'

FROM ubuntu:18.04
LABEL maintainer="fcouto@di.fc.ul.pt"

# Labels
LABEL org.label-schema.description="MER (Minimal Named-Entity Recognizer)"
LABEL org.label-schema.url="http://labs.rd.ciencias.ulisboa.pt/mer/"
LABEL org.label-schema.vcs-url="https://github.com/lasigeBioTM/MER"
LABEL org.label-schema.docker.cmd="docker run -it --rm --name mer-container fjmc/mer-image ./test.sh"


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
COPY . .

RUN apt-get autoremove
RUN apt-get clean
