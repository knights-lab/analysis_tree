import pandas as pd
import qiime2
from qiime2.plugins.taxa.methods import collapse
from pathlib import Path

from qiime2.plugins.composition.visualizers import ancom
from qiime2.plugins.composition.methods import add_pseudocount


# do experiment
levels = [5, 6, 7]
# Set up the working directory
working_dir = Path("./data/processed/16S/shi7_learning/fastqs_stitched")
art_metadata = qiime2.Metadata.load(working_dir / Path("metadata.tsv"))

def run_experiment(levels, filter_names, working_dir, art_metadata):
    for filter_name in filter_names:
        filter_table = qiime2.Artifact.load(working_dir / Path(f"filter_table_{filter_name}.qza"))
        filter_tax = qiime2.Artifact.load(working_dir / Path(f"filter_tax_{filter_name}.qza"))

        for level in levels:
            art_collapse = collapse(filter_table, filter_tax, level).collapsed_table

            df = art_collapse.view(pd.DataFrame)
            s = set([_ for _ in df.columns if _.split(";")[-1] == "__"])

            low_prevalence = df.columns[((df > 0).sum(axis=0) / df.shape[0]) <= .25]

            for _ in low_prevalence:
                s.add(_)

            df = df.loc[:, ~df.columns.isin(s)]
            print(df.shape)
            art_collapse = qiime2.Artifact.import_data("FeatureTable[Frequency]", df)

            art_comp = add_pseudocount(art_collapse).composition_table

            ancom_r = ancom(art_comp, art_metadata.get_column('category')).visualization
            ancom_r.save(str(working_dir / Path(f"ancom_l{level}_{filter_name}.qzv")))

        pc_dir = working_dir / Path(f"q2-picrust2_output_{filter_name}")

        ec_table = qiime2.Artifact.load(pc_dir / Path("ec_metagenome.qza"))
        ko_table = qiime2.Artifact.load(pc_dir / Path("ko_metagenome.qza"))
        pathway_abundance_table = qiime2.Artifact.load(pc_dir / Path("pathway_abundance.qza"))

        for name, table in zip(("ec", "ko", "pa"), (ec_table, ko_table, pathway_abundance_table)):
            df = table.view(pd.DataFrame)
            s = set()

            low_prevalence = df.columns[((df > 0).sum(axis=0) / df.shape[0]) <= .25]

            for _ in low_prevalence:
                s.add(_)

            df = df.loc[:, ~df.columns.isin(s)]

            table_f = qiime2.Artifact.import_data("FeatureTable[Frequency]", df)

            table_comp = add_pseudocount(table_f).composition_table
            ancom_r = ancom(table_comp, art_metadata.get_column('category')).visualization
            ancom_r.save(str(working_dir / Path(f"ancom_{name}_{filter_name}.qzv")))


run_experiment(levels, ["50", "20"], working_dir, art_metadata)
