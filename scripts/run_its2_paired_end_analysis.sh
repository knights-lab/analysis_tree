#!/usr/bin/env bash
scripts/make_manifest_metadata.py \
  data/processed/ITS2 data/processed/ITS2/fastq_manifest.csv \
  data/processed/ITS2/metadata.tsv

cd data/processed/ITS2

qiime tools import \
  --type "SampleData[PairedEndSequencesWithQuality]" \
  --input-path fastq_manifest.csv \
  --output-path demux.qza \
  --input-format PairedEndFastqManifestPhred33

qiime cutadapt trim-paired \
  --i-demultiplexed-sequences demux.qza \
  --p-front-f TCGATGAAGAACGCAGCG \
  --p-front-r TCCTCCGCTTATTGATATGC \
  --o-trimmed-sequences demux-trimmed.qza

qiime demux summarize \
 --i-data demux.qza \
 --o-visualization demux.qzv

qiime demux summarize \
 --i-data demux-trimmed.qza \
 --o-visualization demux-trimmed.qzv

qiime dada2 denoise-paired \
  --i-demultiplexed-seqs demux-trimmed.qza \
  --p-trim-left-f 0 \
  --p-trunc-len-f 220 \
  --p-trim-left-r 13 \
  --p-trunc-len-r 200 \
  --o-table dada2-paired-end-table.qza \
  --o-representative-sequences dada2-paired-end-rep-seqs.qza \
  --o-denoising-stats dada2-paired-end-stats.qza

qiime metadata tabulate \
  --m-input-file dada2-paired-end-stats.qza \
  --o-visualization dada2-paired-end-stats.qzv

qiime feature-classifier classify-sklearn \
  --i-classifier ../unite/unite-ver8-99-classifier-02.02.2019.qza \
  --i-reads dada2-paired-end-rep-seqs.qza \
  --o-classification taxonomy-paired-end.qza

qiime taxa barplot \
  --i-table dada2-paired-end-table.qza \
  --i-taxonomy taxonomy-paired-end.qza \
  --m-metadata-file metadata.tsv \
  --o-visualization taxa-bar-paired-end-plots.qzv
