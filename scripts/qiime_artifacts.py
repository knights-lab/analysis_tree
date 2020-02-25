import pandas as pd
import qiime2
from qiime2.plugins.taxa.methods import collapse
from qiime2.plugins.taxa.visualizers import barplot

from pathlib import Path

working_dir = Path("./data/processed/ITS2/shi7_learning/fastqs")

art_table = qiime2.Artifact.load(working_dir / Path("dada2-single-end-table.qza"))
df_table = art_table.view(pd.DataFrame)


art_tax = qiime2.Artifact.load(working_dir / Path("taxonomy-single-end.qza"))
df_tax = art_tax.view(pd.DataFrame)

art_metadata = qiime2.Metadata.load(working_dir / Path("metadata.tsv"))
df_metadata = art_metadata.to_dataframe()

s_blank_names = {_ for _ in df_metadata.query("category == 'NA'").index}
mask_seq_ids = (df_table.loc[s_blank_names, :].sum(axis=0) > 0)

s_seq_ids = set(df_tax.loc[mask_seq_ids & ~(df_tax["Taxon"].str.contains("f__Fomitopsidaceae") | df_tax["Taxon"].str.contains("f__Polyporaceae")), :].index)

df_filter_table = df_table.loc[~df_table.index.isin(s_blank_names), ~df_table.columns.isin(s_seq_ids)]
art_filter_table = qiime2.Artifact.import_data("FeatureTable[Frequency]", df_filter_table)


df_filter_tax = df_tax.loc[~df_tax.index.isin(s_seq_ids), :]
art_filter_tax = qiime2.Artifact.import_data("FeatureData[Taxonomy]", df_filter_tax)

df_metadata = df_metadata.loc[~df_metadata.index.isin(s_blank_names), :]

art_collapse_species = collapse(art_filter_table, art_filter_tax, 5).collapsed_table
df_collapse_species = art_collapse_species.view(pd.DataFrame)

df_collapse_species_ra = df_collapse_species.apply(lambda x: x / sum(x), axis=1)

df_sub = df_collapse_species_ra.loc[:, (df_collapse_species_ra.columns.str.contains("f__Polyporaceae") | df_collapse_species_ra.columns.str.contains("f__Fomitopsidaceae"))]

import matplotlib.pyplot as plt
# for group, df in df_sub.join(df_metadata).groupby("category"):
#     fig, ax = plt.subplots()
#     df.plot(kind="bar", stacked=True, ax=ax)
#     ax.legend().remove()
#     plt.show()

fig, ax = plt.subplots()
df_sub.plot(kind="bar", stacked=True, ax=ax)
ax.legend().remove()
plt.show()

# fig, ax = plt.subplots()
# df_collapse_species_ra.plot(kind="bar", stacked=True, ax=ax)
# ax.legend().remove()
# plt.show()

#
# for group, df in df_sub.join(df_metadata).groupby("category"):
#     if group == "Ff":
#         mask_ff = df.loc[:, 'k__Fungi;p__Basidiomycota;c__Agaricomycetes;o__Polyporales;f__Polyporaceae;g__Fomes;s__Fomes_fomentarius'] >= .2
#     if group == "Pb":
#         mask_pb =

#
# df_its2_table: pd.DataFrame = qiime2.Artifact.\
#     load("./data/processed/ITS2/shi7_learning/fastqs/dada2-single-end-table.qza").\
#     view(pd.DataFrame)
#
# (df_its2_table.loc["BLANK.001.B04.ITS2.S156", :] > 0).sum()
# (df_its2_table.loc["BLANK.001.C04.ITS2.S164", :] > 0).sum()
#
# # this blank is showing some OTUs that do appear in sequences
# df_its2_table.loc[:, df_its2_table.loc["BLANK.001.B04.ITS2.S156", :] > 0].sum(axis=1)
#
# df_its2_table.loc[:, df_its2_table.loc["BLANK.001.C04.ITS2.S164", :] > 0].sum(axis=1)
#
#
# #%%
# # grab the problem otus
# problem_seqs = df_its2_table.columns[df_its2_table.loc["BLANK.001.B04.ITS2.S156", :] > 0]
#
# # Let us grab their taxonomy
# art_its2_tax = qiime2.Artifact.\
#     load("./data/processed/ITS2/shi7_learning/fastqs/taxonomy-single-end.qza")
# df_its2_tax: pd.DataFrame = art_its2_tax.view(pd.DataFrame)
#
# blank_seqs = [_ for _ in df_its2_tax.loc[problem_seqs, "Taxon"]]
#
# # We need to keep the Pb, the rest of them can go
# problem_seqs = {_ for _ in problem_seqs}
# problem_seqs.discard('2f7b8401581d232fbafcdcc0f75e527a')
#
# for _ in df_its2_table.columns[df_its2_table.loc["BLANK.001.C04.ITS2.S164", :] > 0]:
#     problem_seqs.add(_)
#
# # Taxon confidences
# df_its2_tax.loc[df_its2_tax['Taxon'].str.contains('betulinus')]
# # This seems to be ok, let us drop them
# blanks = {"BLANK.001.B04.ITS2.S156", "BLANK.001.C04.ITS2.S164"}
# df_its2_filter = df_its2_table.loc[~df_its2_table.index.isin(blanks), ~df_its2_table.columns.isin(problem_seqs)]
# art_filter_its2 = qiime2.Artifact.import_data("FeatureTable[Frequency]", df_its2_filter)
#
# art_metadata = qiime2.Metadata.\
#     load("./data/processed/ITS2/shi7_learning/fastqs/metadata.tsv")
#
# art_collapse_species = collapse(art_filter_its2, art_its2_tax, 7)[0]
#
# vis_tax_its2 = barplot(art_filter_its2, art_its2_tax, art_metadata)
#
#
# df_art_collapse = art_collapse_species.view(pd.DataFrame)
#
# df_art_collapse = df_art_collapse.apply(lambda x: x / sum(x), axis=1)
#
# df_art_collapse.loc[:, df_art_collapse.columns.str.contains("betulinus")]
