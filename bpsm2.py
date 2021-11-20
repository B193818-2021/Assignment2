import subprocess
import shutil
import os
import re

# define pullseq path  hear
PULLSEQ = '/Users/andy/Documents/HomeWorks/Assignment2/pullseq'

print('Pipeline start')

################################################################
# Part 1: Preprocess
################################################################

## Create workspace
while True:
    # ask for workspace
    workspace = input('Please input a dir for workspace:')
    if not workspace:  # handle empty input
        print('Empty input!')
        continue
    # ask if user want to overwrite exist workspace
    if os.path.isdir(workspace):
        ow = input('Warning: Workspace already exists, overwrite?(yes):')
        if ow == 'y' or ow == 'yes':  # overwrite existing workspace
            shutil.rmtree(workspace)
        else:  # ask for another workspace
            print('Another workspace needed!')
            continue
    print('All output will be written to "{}".'.format(workspace))
    # make directory
    os.makedirs(workspace)
    break

## Ask for protein family
while True:
    protein = input('Please input a protein family:')
    if not protein:  # handle empty input
        print('Empty input!')
        continue
    break

## Ask for taxonomic group
while True:
    taxonomy = input('Please input a taxonomic group:')
    if not taxonomy:  # handle empty input
        print('Empty input!')
        continue
    break

## Download sequences
# build path for efetch result
fasta = '{}/protein-sequences.fa'.format(workspace)
# build efetch arguments, set stop option to download only users limited number of sequences
args = ['efetch', '-format', 'fasta', '-stop', str(stop)]
# use esearch output as stdin and save efetch result as a fasta file
with open(direct, 'r') as stdin, open(fasta, 'w') as stdout:
    # call efetch
    subprocess.check_call(args, stdin=stdin, stdout=stdout)
print('Protein sequences saved in "{}".'.format(fasta))

## Count species
# build regex to match species in fasta file, which is surrounded by []
seq_name_re = re.compile(r'^>.+?\[(.*)\]')
# set used to collect species name
seq_names = set()
# read fasta file
with open(fasta, 'r') as f:
    for seq_line in f:  # loop through each line in fasta file
        # try to match a sequence header
        seq_name_match = seq_name_re.match(seq_line)
        if seq_name_match:  # this line is a sequence header
            # add species name to collect set
            seq_names.add(seq_name_match.group(1))
# count unique species name
species = len(seq_names)
# ask if user wants to continue
goon = input(
    'These sequences come from {} species. Continue?(yes)'.format(species))
if goon != 'y' and goon != 'yes':  # terminate by user
    print('Pipeline terminate!')
    os.exit(0)

################################################################
# Part 3: Analysis
################################################################

## Align sequences
print('Aligning sequences ...')
# build path for MSA result
align = '{}/protein-sequences-align.fa'.format(workspace)
# build clustalo arguments
args = ['clustalo', '-i', fasta, '-o', align, '-v']
# call clustalo
subprocess.check_call(args)
print('Alignment result saved in: "{}"'.format(align))

## Ask if user wants to scale down sequences
print(
    'Note: analysis conservation for too many sequences will take a long time.'
)
while True:
    num = input(
        'Please input a number of sequences you want to continue analysis:(Enter directly to use all)'
    )
    if num:  # user input
        try:  # try to convert user input as int
            num = int(num)
        except ValueError:  # user input is not numeric
            print('Invalid value as a number "{}"'.format(num))
            continue
    else:  # handle empty input, set stop as download sequences number
        num = stop
    break

## Scale down sequences
if num >= stop:  # user input a larger number
    analysis_seq = align
    print('Analysis all of {} sequences'.format(stop))
else:  # user wants to scale down sequences
    print('Analysis most similar {} sequences'.format(num))
    # info = '{}/protein-sequences-info.txt'.format(workspace)
    # args = ['infoalign', '-sequence', align, '-outfile', info]
    # subprocess.check_call(args)
    # build path for consensus sequence
    cons = '{}/protein-sequences-cons.fa'.format(workspace)
    # build cons arguments
    args = ['cons', '-sequence', align, '-outseq', cons]
    # call cons
    subprocess.check_call(args)
    print('Consensus sequences saved in: "{}"'.format(cons))

    # make blast db and blast sequence
    print('Making blast db ...')
    # build path for blast db
    db = '{}/protein-sequences-db'.format(workspace)
    # build makeblastdb arguments
    args = ['makeblastdb', '-in', fasta, '-dbtype', 'prot', '-out', db]
    # call makeblastdb
    subprocess.check_call(args)
    print('Blast all sequences ...')
    # build path for blastp result
    blastp = '{}/protein-sequences-blastp.txt'.format(workspace)
    # build blastp arguments
    args = [
        'blastp', '-db', db, '-query', cons, '-outfmt', '7', '-max_hsps', '1'
    ]
    # save blastp result to file
    with open(blastp, 'w') as stdout:
        # call blastp
        subprocess.check_call(args, stdout=stdout)
    print('Blastp result saved in: "{}"'.format(blastp))

    # collect bit score and sequence name
    seq_names = []
    # read blastp result
    with open(blastp, 'r') as f:
        for seq_line in f:  # loop through blastp result
            if not seq_line.startswith('#'):  # skip header
                seq_line = seq_line.strip().split('\t')  # split fields
                # collect bit score and sequence name
                seq_names.append((float(seq_line[11]), seq_line[1]))
    # sorted by bit score and extract most highest bit score sequences
    seq_names = sorted(seq_names, reverse=True)[:num]
    # output most similarly sequence name
    order = '{}/protein-sequences-order.txt'.format(workspace)
    with open(order, 'w') as f:
        for _, name in seq_names:  # only output sequence name
            f.write('{}\n'.format(name))
    # build path for pullseq output
    analysis_seq = '{}/protein-sequences-analysis.fa'.format(workspace)
    # build pullseq arguments
    args = [PULLSEQ, '-i', align, '-n', order]
    # write pullseq output to a file
    with open(analysis_seq, 'w') as stdout:
        # call pullseq
        subprocess.check_call(args, stdout=stdout)
    print('Analysis sequence saved in: "{}"'.format(analysis_seq))
## plotcon
# ask for window size
while True:
    ws = input('Please input the window size:')
    try:  # make sure user input is numeric
        ws = int(ws)
    except ValueError:  # user input is not numeric, handel empty input, too
        print('Invalid window size: "{}"'.format(ws))
    print('Using window size: "{}"'.format(ws))
    break
# build plotcon arguments
args = [
    'plotcon', '-graph', 'svg', '-winsize',
    str(ws), '-sequence',
    os.path.abspath(analysis_seq)
]
# call plotcon and capture stdout
stdout = subprocess.check_output(args, cwd=workspace).decode()
# plotcon can not set output path option
# so we need to extract output path from stdout
# using regex extract the output path for the svg format image
outsvg = '{}/{}'.format(workspace, re.search(r'\S+\.svg', stdout).group())
print('Plotcon output image saved in: "{}"'.format(outsvg))

## Scan motif
print('Scaning motif ...')
# patmatmotifs only work for separate fasta file
# so we need to separate protein sequence in a lot of files
# make directory to save fasta files
motif_dir = '{}/motif'.format(workspace)
os.mkdir(motif_dir)
# regex use to match fasta sequence header and extract sequence name
seq_name_re = re.compile(r'^>(\S+)\s.*')
# regex to extract motif name
motif_re = re.compile(r'Motif = (\S+)')
# set use to collect motif names
motifs = set()
# read downloaded protein sequences
with open(fasta, 'r') as f:
    seq_line = f.readline()  # read first line
    # this should be sequence header
    seq_name_match = seq_name_re.match(seq_line)
    while seq_line:  # loop through each sequence
        # sequence name line has been read in
        seq_name = seq_name_match.group(1)  # extract sequence name
        # build path for this sequence
        seq_path = '{}/{}.fa'.format(motif_dir, seq_name)
        # write sequence contents to a new separate fasta file
        with open(seq_path, 'w') as seq_file:
            # output sequence header line first
            seq_file.write(seq_line)
            # keep going through this sequence content, until we hit next sequence header
            while True:
                seq_line = f.readline()  # read next line
                if seq_line:  # read something, file is not ending
                    # check if we hit next sequence header
                    seq_name_match = seq_name_re.match(seq_line)
                    if seq_name_match:  # hit next sequence header, end of this sequence
                        break
                    else:
                        seq_file.write(seq_line)
                else:  # read nothing, file is ending, end reading
                    break
        # sequence saved in a separate fasta file, next step
        # build path for motif scan result
        motif_path = '{}/{}.patmatmotifs'.format(motif_dir, seq_name)
        # build patmatmotifs arguments
        args = ['patmatmotifs', '-sequence', seq_path, '-outfile', motif_path]
        # call patmatmotifs
        subprocess.check_call(args)
        # read patmatmotifs
        with open(motif_path) as motif_file:
            for motif_line in motif_file:  # loop through the file
                # match and extract motifs
                motif_match = motif_re.match(motif_line)
                if motif_match:  # found the motif name
                    # add motif name to collection
                    motifs.add(motif_match.group(1))
print('Found {} motif:'.format(len(motifs)))
# output all unique motifs
motif = '{}/protein-sequences-motifs.txt'.format(workspace)
with open(motif, 'w') as f:
    for m in motifs:
        print(m)  # report to screen
        f.write('{}\n'.format(motif))  # write to file
print('Motif list saved to: {}'.format(motif))
