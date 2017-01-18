#!/bin/bash

cd data

ls *[^0-9s].txt | xargs -l ../produce_data_files.sh

cd ..
