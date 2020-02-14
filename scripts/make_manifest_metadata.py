#!/usr/bin/env python
import sys
from glob import glob
import os
import csv
import re


def format_basename(filename):
    return re.sub('[^0-9a-zA-Z]+', '.', '.'.join(os.path.basename(filename).split('.')[:-1])).strip(".")


def main(input_folder: str, outfp_manifest: str, outfp_metadata: str) -> None:
    files = glob(f"{input_folder}/*.fq")
    # basenames = [format_basename(_) for _ in files]
    fp_forward = [os.path.realpath(_) for _ in files if ".R1." in _ or "_R1_" in _]
    name_forward = [format_basename(_.replace(".R1.", "")) for _ in files if ".R1." in _ or "_R2_" in _]

    fp_reverse = [os.path.realpath(_) for _ in files if ".R2." in _ or "_R2_" in _]
    name_reverse = [format_basename(_.replace(".R2.", "")) for _ in files if ".R2." in _ or "_R2_" in _]

    with open(outfp_manifest, "w") as outf_manifest:
        csv_out = csv.writer(outf_manifest)
        csv_out.writerow(["sample-id", "absolute-filepath", "direction"])
        for name, fp in zip(name_forward, fp_forward):
            csv_out.writerow([name, fp, "forward"])
        for name, fp in zip(name_reverse, fp_reverse):
            csv_out.writerow([name, fp, "reverse"])

    with open(outfp_metadata, "w") as outf_metada:
        csv_out = csv.writer(outf_metada, delimiter="\t")
        csv_out.writerow(["sample-id",	"category"])
        csv_out.writerow(["#q2:types",	"categorical"])
        for name in name_forward:
            if ".Pb." in name:
                cat = "Pb"
            elif ".Ff." in name or ".F." in name:
                cat = "Ff"
            else:
                cat = "NA"
            csv_out.writerow([name, cat])


if __name__ == "__main__":
    input_folder = sys.argv[1]
    outf = sys.argv[2]
    outf_metada = sys.argv[3]
    main(input_folder, outf, outf_metada)
