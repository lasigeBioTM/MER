#!/bin/bash

cd data

ls | grep -Ev 'README.*|*_words?1?2?.txt' | xargs -l ../produce_data_files.sh

cd ..
