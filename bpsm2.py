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
