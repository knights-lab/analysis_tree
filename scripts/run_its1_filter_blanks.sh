#!/usr/bin/env bash
#This whole process would be easier done in the artifact API
cd /mnt/data/code/analysis_tree/data/processed/ITS1/shi7_learning/fastqs

#First grab the
qiime feature-table filter-samples \
  --i-table dada2-single-end-table.qza \
  --m-metadata-file metadata.tsv \
  --p-where '"category" IN ("NA")' \
  --o-filtered-table dada2-single-end-table-blanks.qza
# Note, the single vs double quotes matter above!

#qiime feature-table summarize \
#  --i-table dada2-single-end-table-blanks.qza \
#  --o-visualization dada2-single-end-table-blanks.qzv

#qiime tools view dada2-single-end-table-blanks.qzv
# Note, you could also take a look at this file at view.qiime2.org, your call!

# First, remove the blanks from the feature table
qiime feature-table filter-seqs \
  --i-data dada2-single-end-rep-seqs.qza \
  --m-metadata-file metadata.tsv \
  --p-where '"category" IN ("NA")' \
  --p-exclude-ids \
  --o-filtered-data dada2-single-end-rep-seqs-sans-blanks.qza

qiime feature-table filter-seqs \
  --i-data dada2-single-end-rep-seqs.qza \
  --m-metadata-file metadata.tsv \
  --p-where '"category" IN ("NA")' \
  --p-exclude-ids \
  --o-filtered-data dada2-single-end-rep-seqs-sans-blanks.qza

# Then, remove the features that are identified in `features-to-filter.tsv`
qiime feature-table filter-seqs \
  --i-data dada2-single-end-rep-seqs-sans-blanks.qza \
  --i-table dada2-single-end-table-blanks.qza \
  --p-exclude-ids \
  --o-filtered-data filtered-rep-seqs.qza

# This isn't necessary, just want to view the stats about our `filtered-table.qza`
#qiime feature-table summarize \
#  --i-table filtered-table.qza \
#  --o-visualization filtered-table.qzv
