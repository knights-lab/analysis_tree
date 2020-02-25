#!/usr/bin/env bash
cd /mnt/data/code/analysis_tree/data/processed/ITS1/shi7_learning/fastqs

qiime dada2 denoise-single \
  --i-demultiplexed-seqs demux-trimmed.qza \
  --p-trim-left 0 \
  --p-trunc-len 220 \
  --o-representative-sequences dada2-single-end-rep-seqs.qza \
  --o-table dada2-single-end-table.qza \
  --o-denoising-stats dada2-single-end-stats.qza

qiime metadata tabulate \
  --m-input-file dada2-single-end-stats.qza \
  --o-visualization dada2-single-end-stats.qzv

qiime feature-classifier classify-sklearn \
  --i-classifier ../../../unite/unite-ver8-99-classifier-02.02.2019.qza \
  --i-reads dada2-single-end-rep-seqs.qza \
  --o-classification taxonomy-single-end.qza

qiime taxa barplot \
  --i-table dada2-single-end-table.qza \
  --i-taxonomy taxonomy-single-end.qza \
  --m-metadata-file metadata.tsv \
  --o-visualization taxa-bar-single-end-plots.qzv
