#!/usr/bin/env bash
#conda activate qiime2-2019.10
cd /mnt/data/code/analysis_tree/data/processed/16S/shi7_learning/fastqs_stitched

qiime picrust2 full-pipeline \
   --i-table filter_table_50.qza \
   --i-seq dada2-single-end-rep-seqs.qza \
   --output-dir q2-picrust2_output_50 \
   --p-threads 32 \
   --p-hsp-method mp \
   --p-max-nsti 2 \
   --verbose

qiime picrust2 full-pipeline \
  --i-table filter_table_20.qza \
  --i-seq dada2-single-end-rep-seqs.qza \
  --output-dir q2-picrust2_output_20 \
  --p-threads 32 \
  --p-hsp-method mp \
  --p-max-nsti 2 \
  --verbose
