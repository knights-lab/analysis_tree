import pandas as pd
import qiime2
from qiime2.plugins.taxa.methods import collapse
from qiime2.plugins.diversity.methods import beta_phylogenetic
from qiime2.plugins.diversity.methods import alpha
from qiime2.plugins.diversity.visualizers import alpha_group_significance
from qiime2.plugins.diversity.methods import beta
from qiime2.plugins.diversity.visualizers import beta_group_significance
from qiime2.plugins.phylogeny.pipelines import align_to_tree_mafft_fasttree
import matplotlib.pyplot as plt
from pathlib import Path

# Set up the working directory
working_dir = Path("./data/processed/16S/shi7_learning/fastqs_stitched")

# load in the single-end table from dada2
art_table = qiime2.Artifact.load(working_dir / Path("dada2-single-end-table.qza"))
df_table = art_table.view(pd.DataFrame)

# load in the taxonomy single end
art_tax = qiime2.Artifact.load(working_dir / Path("taxonomy-single-end.qza"))
df_tax = art_tax.view(pd.DataFrame)

# load in the artifact metadata
art_metadata = qiime2.Metadata.load(working_dir / Path("metadata.tsv"))
df_metadata = art_metadata.to_dataframe()

art_repseqs = qiime2.Artifact.load(working_dir / Path("dada2-single-end-rep-seqs.qza"))

# filter down to the blanks
s_blank_names = {_ for _ in df_metadata.query("category == 'NA'").index}
mask_seq_ids = (df_table.loc[s_blank_names, :].sum(axis=0) > 0)

# filter out the not majority samples
sample_filters = {
    "50": {
        "1.Ff.1",
        "25.Pb.4",
        "24.Pb.3",
        "3.Ff.3",
        "21.Pb.Z",
        "18.Pb.E",
        "5.Ff.5",
        "6.Ff.6",
        "2.Ff.2",
        "23.Pb.2",
        "19.Pb.F",
        "14.Pb.A",
        "12.Ff.F",
        "22.Pb.1"
     },
    "20": {
        "1.Ff.1",
        "25.Pb.4",
        "24.Pb.3",
        "3.Ff.3",
        "21.Pb.Z",
        "18.Pb.E",
        "5.Ff.5",
        "6.Ff.6",
        "2.Ff.2",
        "23.Pb.2",
        "19.Pb.F",
        "14.Pb.A",
        "12.Ff.F",
        "22.Pb.1"
        "13.F.G",
        "17.Pb.D",
        "20.Pb.G"
    }
}

for filter_name in sample_filters.keys():
    s_names = sample_filters[filter_name]

    s_filter_names = {_ for _ in df_metadata.index if ".".join(_.split(".")[:3]) in s_names}

    # s_seq_ids = set(df_tax.loc[mask_seq_ids & ~(df_tax["Taxon"].str.contains("f__Fomitopsidaceae") | df_tax["Taxon"].str.contains("f__Polyporaceae")), :].index)
    s_seq_ids = set(df_tax.loc[mask_seq_ids, :].index)

    df_filter_table = df_table.loc[df_table.index.isin(s_filter_names), ~df_table.columns.isin(s_seq_ids)]
    # df_filter_table = df_table.loc[~df_table.index.isin(s_blank_names), :]
    art_filter_table = qiime2.Artifact.import_data("FeatureTable[Frequency]", df_filter_table)


    df_filter_tax = df_tax.loc[~df_tax.index.isin(s_seq_ids), :]
    # df_filter_tax = df_tax.copy()
    art_filter_tax = qiime2.Artifact.import_data("FeatureData[Taxonomy]", df_filter_tax)

    df_metadata = df_metadata.loc[df_metadata.index.isin(s_filter_names), :]

    chao1_ad = alpha(art_filter_table, metric='chao1').alpha_diversity
    shannon_ad = alpha(art_filter_table, metric='shannon').alpha_diversity


    alpha_group_significance_chao1 = alpha_group_significance(chao1_ad, art_metadata).visualization
    alpha_group_significance_shannon = alpha_group_significance(shannon_ad, art_metadata).visualization

    chao1_ad.save(str(working_dir / Path(f"chao1_{filter_name}.qza")))
    shannon_ad.save(str(working_dir / Path(f"shannon_{filter_name}.qza")))
    alpha_group_significance_chao1.save(str(working_dir / Path(f"chao1_{filter_name}.qzv")))
    alpha_group_significance_chao1.save(str(working_dir / Path(f"shannon_{filter_name}.qzv")))

    aitchison = beta(art_filter_table, metric='aitchison', pseudocount=1).distance_matrix
    ait_sg = beta_group_significance(aitchison, art_metadata.get_column('category'), method="anosim").visualization
    aitchison.save(str(working_dir / Path(f"ait_{filter_name}.qza")))

    r_tree = align_to_tree_mafft_fasttree(sequences=art_repseqs, n_threads=32)

    phylogentic_beta = beta_phylogenetic(art_filter_table, r_tree.rooted_tree, "unweighted_unifrac")
    unifrac_sg = beta_group_significance(phylogentic_beta.distance_matrix, art_metadata.get_column('category'), "anosim").visualization
    unifrac_sg.save(str(working_dir / Path(f"unifrac_{filter_name}.qzv")))

    art_filter_table.save(str(working_dir / Path(f"filter_table_{filter_name}.qza")))
    art_filter_tax.save(str(working_dir / Path(f"filter_tax_{filter_name}.qza")))
