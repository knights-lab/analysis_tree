#!/usr/bin/env python
# make_manifest_single_end.py <input_folder> <output_file_manifest> <output_file_metadata>
import sys
from glob import glob
import os
import csv
import re


def format_basename(filename):
    return re.sub('[^0-9a-zA-Z]+', '.', '.'.join(os.path.basename(filename).split('.')[:-1])).strip(".")


def main(input_folder: str, outfp_manifest: str, outfp_metadata: str) -> None:
    files = glob(f"{input_folder}/*.fq")
    files = [os.path.realpath(_) for _ in files]
    names = [format_basename(_) for _ in files]

    with open(outfp_manifest, "w") as outf_manifest:
        csv_out = csv.writer(outf_manifest)
        csv_out.writerow(["sample-id", "absolute-filepath", "direction"])
        for name, fp in zip(names, files):
            csv_out.writerow([name, fp, "forward"])

    with open(outfp_metadata, "w") as outf_metada:
        csv_out = csv.writer(outf_metada, delimiter="\t")
        csv_out.writerow(["sample-id",	"category"])
        csv_out.writerow(["#q2:types",	"categorical"])
        for name in names:
            if ".Pb." in name:
                cat = "Pb"
            elif (".Ff." in name) or (".F." in name):
                cat = "Ff"
            else:
                cat = "NA"
            csv_out.writerow([name, cat])


if __name__ == "__main__":
    input_folder = sys.argv[1]
    outf = sys.argv[2]
    outf_metada = sys.argv[3]
    main(input_folder, outf, outf_metada)
