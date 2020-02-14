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

Had to re-run the entire paired-end analysis because I included non-alphanumeric characters in the sample names.
Compiled the analysis into a script, and it appears to have failed to assign taxonomy to all things but the BLANKS.
I have a hunch that the leading 0s are what is causing us to lose the samples.
To strip them, you can run this `str.strip()` in the format basenames code.
Nevertheless, I am going to attempt to align them with pre-made naive bayes database.

### UNITE 7

Download the database
```bash
wget https://s3-us-west-2.amazonaws.com/qiime2-data/community-contributions-data-resources/2018.11-unite-classifier/unite-ver7-99-classifier-01.12.2017.qza
```

I paused this for now, results are back in from without this step and removing the leading period seemed to work.

The ITS1 analysis looks good to me, Pb and Ff are what we expected.

To run the entire analysis for ITS1 simply run the command.

```bash
scripts/run_its1_paired_end_analysis.sh
scripts/run_its1_single_end_analysis.sh
```

```bash
scripts/run_its2_paired_end_analysis.sh
scripts/run_its2_single_end_analysis.sh
```

We will also want to re-run the analysis with cutadapt + SHI7 + BURST alignment.

```bash
#TODO: Next step, is to run the 16S analysis with DADA2 and QIIME2.
#TODO: Ask Jonathon what the length of the amplicon region is.
#TODO Setup a meeting with Jonathon
```


# 16S with pre-analysis using shi7
```bash
# Removing leading _s
for FILE in `ls`; do mv $FILE `echo $FILE | sed -e 's:^_*::'`; done
shi7_learning
shi7_cmd.sh
```

```bash
qiime tools import \
--input-path ./combined_seqs.fna \
--output-path ./combined_seqs.qza \
--type 'SampleData[Sequences]' \
--input-format 'QIIME1DemuxFormat'
```

Rewrote the make manifest script to handle the output from shi7.
```bash
scripts/make_manifest_single_end.py data/processed/16S/shi7_learning/fastqs/ data/processed/16S/shi7_learning/fastqs/fastqmanifest.txt data/processed/16S/shi7_learning/fastqs/metadata.tsv
```

We should double check that the phred33 single-end fastq manifest is the correct way to import into qiime2 from shi7 flash.
```bash
qiime tools import \
 --type "SampleData[JoinedSequencesWithQuality]" \
 --input-path fastqmanifest.txt \
 --output-path demux.qza \
 --input-format SingleEndFastqManifestPhred33
```

```bash
qiime dada2 denoise-single \
  --i-demultiplexed-seqs demux.qza \
  --p-trim-left 0 \
  --p-trunc-len 500 \
  --o-representative-sequences dada2-single-end-rep-seqs.qza \
  --o-table dada2-single-end-table.qza \
  --o-denoising-stats dada2-single-end-stats.qza


```

So I noticed that almost none of the dada2 denoised made it past the stage of chimeric.
We are going to retry by running shi7 no stitching, analyze the quality scores, then run both dada2 paired- and singled-end.

```bash
for f in *.fq; do
    mv -- "$f" "$(basename -- "$f" .fq).fastq"
done


../../../../../scripts/make_manifest_metadata.py ./ ./fastqmanifest.txt ./metadata.txt

qiime tools import \
  --type "SampleData[PairedEndSequencesWithQuality]" \
  --input-path fastqmanifest.txt \
  --output-path paired-end-16S-demux.qza \
  --input-format PairedEndFastqManifestPhred33
```

```bash
qiime demux summarize \
 --i-data paired-end-16S-demux.qza \
 --o-visualization paired-end-16S-demux.qzv
```

```bash
qiime dada2 denoise-paired \
  --i-demultiplexed-seqs paired-end-demux.qza \
  --p-trim-left-f 20 \
  --p-trunc-len-f 240 \
  --p-trim-left-r 20 \
  --p-trunc-len-r 200 \
  --o-table dada2-paired-end-table.qza \
  --o-representative-sequences dada2-paired-end-rep-seqs.qza \
  --o-denoising-stats dada2-paired-end-stats.qza

qiime metadata tabulate \
  --m-input-file dada2-paired-end-stats.qza \
  --o-visualization dada2-paired-end-stats.qzv
```

```bash
qiime dada2 denoise-single \
  --i-demultiplexed-seqs demux-trimmed.qza \
  --p-trim-left 20 \
  --p-trunc-len 240 \
  --o-representative-sequences dada2-single-end-16S-stats.qza \
  --o-table dada2-single-end-16S-table.qza \
  --o-denoising-stats dada2-single-end-16S-stats.qz

qiime metadata tabulate \
  --m-input-file dada2-single-end-16S-stats.qza \
  --o-visualization dada2-single-end-16S-stats.qzv
```

We were able to get more reads out of the paired-end filter sequences by increasing the trimming range.
Let us try this on the shi7 stitched reads instead with higher quality scores.

```bash
qiime dada2 denoise-single \
  --i-demultiplexed-seqs demux.qza \
  --p-trim-left 0 \
  --p-trunc-len 450 \
  --o-representative-sequences dada2-stats.qza \
  --o-table dada2-table.qza \
  --o-denoising-stats dada2-stats.qza

qiime metadata tabulate \
  --m-input-file dada2-stats.qza \
  --o-visualization dada2-stats.qzv

qiime dada2 denoise-single \
  --i-demultiplexed-seqs demux.qza \
  --p-trim-left 20 \
  --p-trunc-len 450 \
  --o-representative-sequences dada2-beg-stats.qza \
  --o-table dada2-beg-table.qza \
  --o-denoising-stats dada2-beg-stats.qza

qiime metadata tabulate \
  --m-input-file dada2-beg-stats.qza \
  --o-visualization dada2-beg-stats.qzv
```

We wanted to detect if it was the beginning or the end of the read that was causing the problems for dada2.

```bash
qiime dada2 denoise-paired \
  --i-demultiplexed-seqs demux.qza \
  --p-trim-left-f 0 \
  --p-trunc-len-f 240 \
  --p-trim-left-r 0 \
  --p-trunc-len-r 200 \
  --o-table dada2-beg-table.qza \
  --o-representative-sequences dada2-beg-rep-seqs.qza \
  --o-denoising-stats dada2-beg-stats.qza

qiime metadata tabulate \
  --m-input-file dada2-beg-stats.qza \
  --o-visualization dada2-beg-stats.qzv

qiime dada2 denoise-paired \
  --i-demultiplexed-seqs demux.qza \
  --p-trim-left-f 20 \
  --p-trunc-len-f 250 \
  --p-trim-left-r 20 \
  --p-trunc-len-r 250 \
  --o-table dada2-beg-table.qza \
  --o-representative-sequences dada2-end-rep-seqs.qza \
  --o-denoising-stats dada2-end-stats.qza

qiime metadata tabulate \
  --m-input-file dada2-end-stats.qza \
  --o-visualization dada2-end-stats.qzv
```
Both the beginning and end of the reads caused a significant amount of reads to be degenerated.

For the final analysis, we will trim both sides.

```bash
qiime dada2 denoise-paired \
  --i-demultiplexed-seqs demux.qza \
  --p-trim-left-f 20 \
  --p-trunc-len-f 240 \
  --p-trim-left-r 20 \
  --p-trunc-len-r 200 \
  --o-table dada2-paired-end-table.qza \
  --o-representative-sequences dada2-paired-end-rep-seqs.qza \
  --o-denoising-stats dada2-paired-end-stats.qza

qiime metadata tabulate \
  --m-input-file dada2-paired-end-stats.qza \
  --o-visualization dada2-paired-end-stats.qzv

qiime dada2 denoise-paired \
  --i-demultiplexed-seqs demux.qza \
  --p-trim-left-f 20 \
  --p-trunc-len-f 240 \  
  --o-table dada2-single-end-table.qza \
  --o-representative-sequences dada2-single-end-rep-seqs.qza \
  --o-denoising-stats dada2-single-end-stats.qza

qiime metadata tabulate \
  --m-input-file dada2-single-end-stats.qza \
  --o-visualization dada2-single-end-stats.qzv
```

So the reason that shi7 doesn't work very well is due to the length of the stiching.
Some of the sequences are longer than the ~250 bp region.
We can fix this with the shi7 stitching mechanism.
There are flags for `--min_overlap`, set to 

```bash
qiime tools import \
--type "SampleData[SequencesWithQuality]" \
--input-path fastqmanifest.csv \
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
```
