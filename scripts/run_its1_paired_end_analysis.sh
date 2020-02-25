#!/usr/bin/env bash
#conda activate qiime2-2019.10
cd /mnt/data/code/analysis_tree/data/processed/ITS1/shi7_learning/fastqs

/mnt/data/code/analysis_tree/scripts/make_manifest_metadata.py \
  ./ \
  ./fastq_manifest.csv \
  ./metadata.tsv

qiime tools import \
  --type "SampleData[PairedEndSequencesWithQuality]" \
  --input-path fastq_manifest.csv \
  --output-path demux.qza \
  --input-format PairedEndFastqManifestPhred33

#qiime cutadapt trim-paired \
#  --i-demultiplexed-sequences demux.qza \
#  # 3' rc of the reverse primer \
#  --p-adapter-f GCANTCGATGAAGAACGCAGC \
#  # 5' forward primer \
#  --p-front-f CTTGGTCATTTAGAGGAAGNTAA \
#  # 5' rc of the forward primer \
#  --p-adapter-r TTANCTTCCTCTAAATGACCAAG \
#  # 3' reverse primer \
#  --p-front-r GCTGCGTTCTTCATCGANTGC \
#  --o-trimmed-sequences demux-trimmed.qza

qiime cutadapt trim-paired \
  --i-demultiplexed-sequences demux.qza \
  --p-adapter-f GCANTCGATGAAGAACGCAGC \
  --p-front-f CTTGGTCATTTAGAGGAAGNTAA \
  --p-adapter-r TTANCTTCCTCTAAATGACCAAG \
  --p-front-r GCTGCGTTCTTCATCGANTGC \
  --o-trimmed-sequences demuxu-trimmed.qza

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
  --i-classifier ../../../unite/unite-ver8-99-classifier-02.02.2019.qza \
  --i-reads dada2-paired-end-rep-seqs.qza \
  --o-classification taxonomy-paired-end.qza

qiime taxa barplot \
  --i-table dada2-paired-end-table.qza \
  --i-taxonomy taxonomy-paired-end.qza \
  --m-metadata-file metadata.tsv \
  --o-visualization taxa-bar-paired-end-plots.qzv
