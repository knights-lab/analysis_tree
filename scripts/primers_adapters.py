its1_f = "CTTGGTCATTTAGAGGAAGNTAA"
its2_r = "GCTGCGTTCTTCATCGANTGC"

inp = "data/processed/ITS1/_1_Ff_1_ITS1_S141_R1_001.fastq"


def read_fastq(fh):
    # Assume linear FASTQS
    count = 0
    while True:
        title = next(fh)
        count += 1
        while title[0] != '@':
            title = next(fh)
        # Record begins
        if title[0] != '@':
            raise IOError('Malformed FASTQ files; verify they are linear and contain complete records - Title line does not begin with "@" symbol - error on line' + str(count) + '.')
        title = title[1:].strip()
        sequence = next(fh).strip()
        count += 1
        garbage = next(fh).strip()
        count += 1
        if garbage[0] != '+':
            raise IOError('Malformed FASTQ files; verify they are linear and contain complete records - strand line does not contain "+" symbol on line' + str(count) + '.')
        qualities = next(fh).strip()
        count += 1
        if len(qualities) != len(sequence):
            raise IOError('Malformed FASTQ files; verify they are linear and contain complete records - Sequence length does not equal quality score length on line ' + str(count) + '.')
        yield title, sequence, qualities


with open(inp, "r") as inf:
    fastq_gen = read_fastq(inf)
    for title, data, qualities in fastq_gen:
        break
