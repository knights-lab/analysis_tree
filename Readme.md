# Build the QIIME2 Database

First step was to select the QIIME2 database.
At first, I am looking at the unite database QIIME2 singletons.
https://unite.ut.ee/repository.php.
It is version number 8, with 9,407 reference sequences.

```bash
wget https://files.plutof.ut.ee/public/orig/51/6F/516F387FC543287E1E2B04BA4654443082FE3D7050E92F5D53BA0702E4E77CD4.zip
```

This oneliner will strip the database of lower letters.
This will help with downstream processing.
```bash
awk '/^>/ {print($0)}; /^[^>]/ {print(toupper($0))}' developer/sh_refs_qiime_ver8_99_02.02.2019_dev.fasta | tr -d ' ' > developer/sh_refs_qiime_ver8_99_02.02.2019_dev_uppercase.fasta
cd ../../raw/processed/unite/
mv ../../raw/unite/qiime2_singletons/developer/sh_refs_qiime_ver8_99_02.02.2019_dev_uppercase.fasta ./
```

Now lets import the sequence and the taxonomy table.
```bash
qiime tools import \
 --type "FeatureData[Sequence]" \
 --input-path ./sh_refs_qiime_ver7_99_02.02.2019_dev_uppercase.fasta \
 --output-path ./unite-ver8-99-seqs-02.02.2019.qza
```

Import the taxonomy data.
```bash
qiime tools import \
 --type "FeatureData[Taxonomy]" \
 --input-path ../../raw/unite/qiime2_singletons/developer/sh_taxonomy_qiime_ver8_99_02.02.2019_dev.txt \
 --output-path ./unite-ver8-99-tax-02.02.2019.qza \
 --input-format HeaderlessTSVTaxonomyFormat
```

Training the classifier, this can take a long time.
```bash
qiime feature-classifier fit-classifier-naive-bayes \
 --i-reference-reads unite-ver8-99-seqs-02.02.2019.qza \
 --i-reference-taxonomy unite-ver8-99-tax-02.02.2019.qza \
 --o-classifier unite-ver8-99-classifier-02.02.2019.qza
```

# Ready up the FASTQ manifest

```bash
scripts/make_manifest_metadata.py data/processed/ITS1 data/processed/ITS1/fastq_manifest.csv data/processed/ITS1/metadata.tsv
```

```bash
qiime tools import \
 --type "SampleData[PairedEndSequencesWithQuality]" \
 --input-path data/processed/ITS1/fastq_manifest.csv \
 --output-path data/processed/ITS1/demux.qza \
 --input-format PairedEndFastqManifestPhred33
```

Check for the front
``
#  --p-adapter-r  \
#  --p-adapter-r  \
`` 

```bash
qiime cutadapt trim-paired \
  --i-demultiplexed-sequences demux.qza \
  --p-front-f CTTGGTCATTTAGAGGAAGNTAA \
  --p-front-r GCTGCGTTCTTCATCGANTGC \
  --o-trimmed-sequences demux-trimmed.qza
```

Removing the primers didn't make the sequences significantly shorter on average (300 vs 281).
For now, the plan is to use dada2 on single-end sequences.
The quality of the sequences tend to siginficantly drop off towards the place the reads should be stitching.

Note for the lab meeting...head to https://view.qiime2.org/ with the two qz files.

## Denoising

To test to see if we lost a majority of our reads in the merging stage, checkout the `qiime2 dada2 denoised paired`.

```bash
qiime dada2 denoise-paired \
 --i-demultiplexed-seqs demux-trimmed.qza \
 --p-trim-left-f 0 \
 --p-trunc-len-f 220 \
 --p-trim-left-r 13 \
 --p-trunc-len-r 200 \
 --o-table dada2-paired-end-table.qza \
 --o-representative-sequences dada2-paired-end-rep-seqs.qza \
 --o-denoising-stats dada2-paired-end-stats.qza
```

And then get the summary statistics.

```bash
qiime metadata tabulate \
 --m-input-file dada2-paired-end-stats.qza \
 --o-visualization dada2-paired-end-stats.qzv
```

And then open up that qzv in the browser.
Note to self, always use qiime2

```bash
qiime feature-classifier classify-sklearn \
 --i-classifier ../unite/unite-ver8-99-classifier-02.02.2019.qza \
 --i-reads dada2-paired-end-rep-seqs.qza \
 --o-classification taxonomy-paired-end.qza
```

Summarize the table for viewing and download the respective qiime2 artifact.

```bash
qiime taxa barplot \
  --i-table dada2-paired-end-table.qza \
  --i-taxonomy taxonomy-paired-end.qza \
  --m-metadata-file metadata.tsv \
  --o-visualization taxa-bar-plots.qzv
```

