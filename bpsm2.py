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
