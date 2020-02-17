#!/usr/bin/env bash
#conda activate qiime2-2019.10
cd /mnt/data/code/analysis_tree/data/processed/16S/shi7_learning/fastqs_stitched

qiime picrust2 full-pipeline \
   --i-table dada2-single-end-table.qza \
   --i-seq dada2-single-end-rep-seqs.qza \
   --output-dir q2-picrust2_output \
   --p-threads 40 \
   --p-hsp-method mp \
   --p-max-nsti 2 \
   --verbose

# Alpha and Beta Diversity Analysis
qiime phylogeny align-to-tree-mafft-fasttree \
  --i-sequences dada2-single-end-rep-seqs.qza \
  --o-alignment aligned-rep-seqs.qza \
  --o-masked-alignment masked-aligned-rep-seqs.qza \
  --o-tree unrooted-tree.qza \
  --o-rooted-tree rooted-tree.qza

qiime diversity core-metrics-phylogenetic \
  --i-phylogeny rooted-tree.qza \
  --i-table dada2-single-end-table.qza \
  --p-sampling-depth 4154 \
  --m-metadata-file metadata.tsv \
  --output-dir core-metrics-results

# Faith Based Alpha-Diversity Analysis
qiime diversity alpha-group-significance \
  --i-alpha-diversity core-metrics-results/faith_pd_vector.qza \
  --m-metadata-file metadata.tsv \
  --o-visualization core-metrics-results/faith-pd-category-significance.qzv

qiime diversity alpha-group-significance \
  --i-alpha-diversity core-metrics-results/evenness_vector.qza \
  --m-metadata-file metadata.tsv \
  --o-visualization core-metrics-results/evenness-category-significance.qzv

# Beta diversity metrics
qiime diversity beta-group-significance \
  --i-distance-matrix core-metrics-results/unweighted_unifrac_distance_matrix.qza \
  --m-metadata-file metadata.tsv \
  --m-metadata-column category \
  --o-visualization core-metrics-results/unweighted-unifrac-category-significance.qzv \
  --p-pairwise

# Need to redo within tree
#qiime diversity beta-group-significance \
#  --i-distance-matrix core-metrics-results/unweighted_unifrac_distance_matrix.qza \
#  --m-metadata-file sample-metadata.tsv \
#  --m-metadata-column subject \
#  --o-visualization core-metrics-results/unweighted-unifrac-category-significance.qzv \
#  --p-pairwise

# Ordination analysis
qiime emperor plot \
  --i-pcoa core-metrics-results/unweighted_unifrac_pcoa_results.qza \
  --m-metadata-file metadata.tsv \
  --o-visualization core-metrics-results/unweighted-unifrac-emperor.qzv

qiime emperor plot \
  --i-pcoa core-metrics-results/bray_curtis_pcoa_results.qza \
  --m-metadata-file metadata.tsv \
  --o-visualization core-metrics-results/bray-curtis-emperor.qzv
