#!/usr/bin/env python
#import argparse
#from glob import glob

#-s /mnt/lfs2/hend6746/devils/samples.txt
#-r /mnt/lfs2/hend6746/devils/fastqFiles_160916/00-RawData
#-b /mnt/lfs2/hend6746/devils/reference/sarHar1.fa

from os.path import join as jp
from os.path import abspath
import os
import sys
import argparse
import commands

parser = argparse.ArgumentParser()
parser.add_argument('-s', "--samples", help="Samples.txt file with sample ID.", required=True)
parser.add_argument('-r', "--rawdata", help="Path to raw fastq data.", required=True)
parser.add_argument('-b', "--bwaindex", help="Path to bwa index file.", required=True)
args = parser.parse_args()

VERBOSE=False

#Function definitions:
def log(txt, out):
    if VERBOSE:
        print(txt)
    out.write(txt+'\n')
    out.flush()

## Read in samples and put them in a list:
samples = []
for l in open(args.samples):
    if len(l) > 1:
        samples.append(l.split('/')[-1].replace('.fastq.1.gz', '').strip())

# Setup folders and paths variables:
resultsDir = abspath('01-Cleaned')
bamFolder = abspath('02-Mapped')
variantFolder = abspath('03-Calls')
PBS_scripts = abspath('PBS_scripts/qc_scripts')
rawdataDir = abspath(args.rawdata)

os.system('mkdir -p %s' % resultsDir)
os.system('mkdir -p %s' % bamFolder)
os.system('mkdir -p %s' % variantFolder)
os.system('mkdir -p %s' % PBS_scripts)

##### Run pipeline ###
for sample in samples:
    print "Processing", sample, "....."
    # Set up files:
    logFile = jp(resultsDir, sample + '_qc.log')
    logCommands = open(jp(PBS_scripts, sample + 'qc_commands.sh'), 'w')

    #Setup for qsub
    log('#!/bin/bash', logCommands)
    log('#PBS -N %s' % sample, logCommands)
    log('#PBS -j oe', logCommands)
    log('#PBS -o %s_job.log' % sample, logCommands)
    log('#PBS -m abe', logCommands)
    log('#PBS -M shendri4@gmail.com', logCommands)
    log('#PBS -q short', logCommands)
    #log('#PBS -l mem=100gb', logCommands)
    log(". /usr/modules/init/bash", logCommands)
    log("module load python/2.7.10", logCommands)
    log("module load bwa", logCommands)
    log("module load grc", logCommands)
    log("module load samtools", logCommands)

###########################################################################
#### Number of raw reads
    cmd = ' '.join(['result = commands.getoutput', '(', 'zcat ', jp(rawdataDir, sample + '.fastq.1.gz'), ' | wc -l', ')']) 
    log(cmd, logCommands)
    
    cmd = ' '.join(['numseqs = int(result) / 4.0'])
    log(cmd, logCommands)
 
    cmd = ' '.join(['print numseqs',
    '>>', logFile, '2>&1'])
    log(cmd, logCommands)
        
#result = commands.getoutput('zcat /mnt/lfs2/hend6746/devils/fastqFiles_160916/01-Cleaned/test_165499_cleaned_SE.fastq.gz | wc -l')
#numseqs = int(result) / 4.0
#print numseqs

# jp(rawdataDir, sample + '.fastq.2.gz'),
#grep "Total pairs:"' + jp(rawdataDir, sample + ), '>>', jp(resultsDir, sample + 'qualityStats_output.txt'), '>>', logFile, '2>&1'])

#Number of cleaned reads
#zcat test_165499_cleaned_PE1.fastq.gz | echo $((`wc -l`/4))

#samtools depth -a

    logCommands.close()