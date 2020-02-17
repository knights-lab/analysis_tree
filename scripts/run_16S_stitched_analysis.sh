#!/usr/bin/env bash
#conda activate qiime2-2019.10
cd /mnt/data/code/analysis_tree/data/processed/16S/shi7_learning/fastqs_stitched

/mnt/data/code/analysis_tree/scripts/make_manifest_single_end.py \
  ./ \
  ./fastq_manifest.csv \
  ./metadata.tsv

qiime tools import \
--type "SampleData[SequencesWithQuality]" \
--input-path fastq_manifest.csv \
--output-path demux.qza \
--input-format SingleEndFastqManifestPhred33

qiime demux summarize \
 --i-data demux.qza \
 --o-visualization demux.qzv

qiime dada2 denoise-single \
  --i-demultiplexed-seqs demux.qza \
  --p-trim-left 0 \
  --p-trunc-len 225 \
  --o-table dada2-single-end-table.qza \
  --o-representative-sequences dada2-single-end-rep-seqs.qza \
  --o-denoising-stats dada2-single-end-stats.qza

qiime metadata tabulate \
  --m-input-file dada2-single-end-stats.qza \
  --o-visualization dada2-single-end-stats.qzv

qiime feature-classifier classify-sklearn \
  --i-classifier ../../../../databases/silva-132-99-515-806-nb-classifier.qza \
  --i-reads dada2-single-end-rep-seqs.qza \
  --o-classification taxonomy-single-end.qza

qiime taxa barplot \
  --i-table dada2-single-end-table.qza \
  --i-taxonomy taxonomy-single-end.qza \
  --m-metadata-file metadata.tsv \
  --o-visualization taxa-bar-single-end-plots.qzv

