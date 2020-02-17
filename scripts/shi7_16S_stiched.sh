#!/usr/bin/env bash
cd /mnt/data/code/analysis_tree/data/processed/16S

for FILE in `ls`; do mv $FILE `echo $FILE | sed -e 's:^_*::'`; done

shi7 --input  ./ \
 --adaptor Nextera \
 --output /mnt/data/code/analysis_tree/data/processed/16S/shi7_learning/fastqs_stitched \
 --flash True \
 --allow_outies False \
 --filter_qual 36 \
 --trim_qual 34 \
 --combine_fasta False \
 --convert_fasta False \
 --min_overlap 280 \
 --max_overlap 300 \
 --filter_length 225
