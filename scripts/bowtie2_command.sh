#!/usr/bin/env bash
bowtie2 --no-unal -x /home/bhillmann/code/analysis_tree/data/processed/unite/ver8_99 -S test.b6 --np 1 --mp 1,1 --rdg "0,1" --score-min "L,0,-0.02" -f scripts/primers/fungal_primers.fna --very-sensitive -p 16 --no-hd -a
