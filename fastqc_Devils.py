#!/usr/bin/env python
#import argparse
#from glob import glob

#-s /mnt/lfs2/hend6746/devils/samples.txt
#-r /mnt/lfs2/hend6746/devils/fastqFiles_160916/00-RawData

from os.path import join as jp
from os.path import abspath
import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-s', "--samples", help="Samples.txt file with sample ID.", required=True)
parser.add_argument('-r', "--rawdata", help="Path to raw fastq data.", required=True)
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
rawdataDir = abspath(args.rawdata)
cleanDir = abspath('01-Cleaned')
bamFolder = abspath('02-Mapped')
variantFolder = abspath('03-Calls')
resultsDir = abspath('fastqc')

os.system('mkdir -p %s' % resultsDir)

##### Run pipeline ###
for sample in samples:
    print "Processing", sample, "....."
    # Set up files:
    logFile = jp(resultsDir, sample + '_fastqc.log')
    logCommands = open(jp(resultsDir, sample + '_fastqc_commands.log'), 'w')

    ######raw
    cmd = ' '.join(['fastqc', '--outdir', resultsDir, '--format fastq', jp(rawdataDir, sample + '.fastq.1.gz'), '>>', logFile, '2>&1']) 
    log(cmd, logCommands)
        
    cmd = ' '.join(['fastqc', '--outdir', resultsDir, '--format fastq', jp(rawdataDir, sample + '.fastq.2.gz'), '>>', logFile, '2>&1'])
    log(cmd, logCommands)
        
    ######cleaned
    cmd = ' '.join(['fastqc', '--outdir', resultsDir, '--format fastq', jp(cleanDir, sample + '_cleaned_PE1.fastq.gz'), '>>', logFile, '2>&1'])
    log(cmd, logCommands)
    
    cmd = ' '.join(['fastqc', '--outdir', resultsDir, '--format fastq', jp(cleanDir, sample + '_cleaned_PE2.fastq.gz'), '>>', logFile, '2>&1'])
    log(cmd, logCommands)
    
    cmd = ' '.join(['fastqc', '--outdir', resultsDir, '--format fastq', jp(cleanDir, sample + '_cleaned_SE.fastq.gz'), '>>', logFile, '2>&1']) 
    log(cmd, logCommands)

#   grep "FastQ paired records kept:" >> qualityStats_output.txt
    ######bam
    #cmd = ' '.join(['fastqc', '--outdir', resultsDir, '--format bam', jp(bamFolder, sample + '.bam'), '>>', logFile, '2>&1'])
    #log(cmd, logCommands)
    
    ######Depth of coverage using GATK
    #cmd = ' '.join([gatkCall,  ' -T DepthOfCoverage ', ' -I ' + jp(bamFolder, sample) + ".bam", 
     #                ' -o ' + jp(variantFolder, sample), '>>', logFile, '2>&1'])
    #log(cmd, logCommands)
   
    logCommands.close()
