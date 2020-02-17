#!/usr/bin/env bash
cd /mnt/data/code/analysis_tree/data/processed/ITS1

for FILE in `ls`; do mv $FILE `echo $FILE | sed -e 's:^_*::'`; done

shi7 --input ./ \
 --adaptor Nextera \
 --output /mnt/data/code/analysis_tree/data/processed/ITS1/shi7_learning/fastqs \
 --flash False \
 --allow_outies False \
 --filter_qual 36 \
 --trim_qual 34 \
 --combine_fasta False \
 --convert_fasta False
