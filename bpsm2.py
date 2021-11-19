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
