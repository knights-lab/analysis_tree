import pandas as pd
import qiime2
from qiime2.plugins.taxa.methods import collapse
from qiime2.plugins.taxa.visualizers import barplot
from qiime2.plugins.diversity.methods import alpha
from qiime2.plugins.diversity.visualizers import alpha_group_significance
from qiime2.plugins.diversity.methods import beta
from qiime2.plugins.diversity.visualizers import beta_group_significance
import matplotlib.pyplot as plt
from pathlib import Path

# Set up the working directory
working_dir = Path("./data/processed/16S/shi7_learning/fastqs_stitched")

# https://docs.qiime2.org/2020.2/tutorials/longitudinal/
# use this to run the paired t-test
# note that the metric should be shannon/chao1
# the group day 0 should be Pb and day 1 should be Ff
# And the metric should be Ff and Pb
