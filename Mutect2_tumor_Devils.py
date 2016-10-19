#!/usr/bin/env python
#import argparse
#from glob import glob

#-s test_normalsamples.txt
#-s test_tumarsamples.txt
#-b /mnt/lfs2/hend6746/devils/reference/sarHar1.fa

from os.path import join as jp
from os.path import abspath
import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-s', "--normalsamples", help="Normal samples.txt file with sample ID.", required=True)
parser.add_argument('-t', "--tumorsamples", help="Tumor samples.txt file with sample ID.", required=True)
parser.add_argument('-b', "--bwaindex", help="Path to bwa index file.", required=True)
#parser.add_argument('-k', "--knownsites", help="Path and fileName of filteredSNP.vcf.", required=True)
args = parser.parse_args()
#args = parser.parse_args('-s samples.txt -r /mnt/lfs2/hend6746/fox_cancer/0rawdata_test -b /mnt/lfs2/hend6746/wolves/reference/canfam31/canfam31.fa'.split())

VERBOSE=False

#Function definitions:
def log(txt, out):
    if VERBOSE:
        print(txt)
    out.write(txt+'\n')
    out.flush()

## Read in samples and put them in a list:
normalsamples = []
for l in open(args.normalsamples):
    if len(l) > 1:
        normalsamples.append(l.split('/')[-1].replace('.fastq.1.gz', '').strip())
#print normalsamples
tumorsamples = []
for l in open(args.tumorsamples):
    if len(l) > 1:
        tumorsamples.append(l.split('/')[-1].replace('.fastq.1.gz', '').strip())
#print tumorsamples

# Setup folders and paths variables:
bamFolder = abspath('02-Mapped')
variantFolder = abspath('03-Calls')
PBS_scripts = abspath('MuTect_PBS_scripts')
normal_PBS_scripts = abspath('MuTect_PBS_scripts/normal_PBS_scripts')
tumor_PBS_scripts = abspath('MuTect_PBS_scripts/tumor_PBS_scripts')
#rawdataDir = abspath(args.rawdata)
bwaIndex = abspath(args.bwaindex)
#knownSites = abspath(args.knownsites)
gatkCall = 'java -jar /opt/modules/biology/gatk/3.5/bin/GenomeAnalysisTK.jar -R %s' % bwaIndex

os.system('mkdir -p %s' % bamFolder)
os.system('mkdir -p %s' % variantFolder)
os.system('mkdir -p %s' % PBS_scripts)
os.system('mkdir -p %s' % normal_PBS_scripts)
os.system('mkdir -p %s' % tumor_PBS_scripts)

##### Run pipeline ###
#for tumorsample in tumorsamples:

for index in xrange(0,len(tumorsamples)):    
# for normalsample in normalsamples:
#     print "Processing", normalsample, "....."
#     # Set up files:
#     logFile = jp(variantFolder, normalsample + '_mutect.log')
#     logCommands = open(jp(normal_PBS_scripts, normalsample + '_mutect_commands.sh'), 'w')
    tumorsample=tumorsamples[index]
    normalsample=normalsamples[index]
    print "Processing", tumorsample, "....."
    # Set up files:
    logFile = jp(variantFolder, tumorsample + '_tumor_mutect.log')
    logCommands = open(jp(tumor_PBS_scripts, tumorsample + '_tumor_mutect_commands.sh'), 'w')

    #Setup for qsub
    log('#!/bin/bash', logCommands)
    log('#PBS -N %s' % tumorsample, logCommands)
    log('#PBS -j oe', logCommands)
    log('#PBS -o %s_job.log' % tumorsample, logCommands)
    log('#PBS -m abe', logCommands)
    log('#PBS -M shendri4@gmail.com', logCommands)
    log('#PBS -q short', logCommands)
    log('#PBS -l mem=100gb', logCommands)
    log(". /usr/modules/init/bash", logCommands)
    log("module load python/2.7.10", logCommands)
    log("module load grc", logCommands)

    ####################
    #Tumor/Normal variant calling
    #NEED TO FIGURE OUT HOW TO CREATE LIST OF TUMOR/NORMAL SAMPLES
    cmd = ' '.join([gatkCall, ' -nct 24 ', ' -T MuTect2 ', ' -I:tumor ' + jp(bamFolder, tumorsample) + '_markdup_BQSR_FIXED.bam', ' -I:normal ' + jp(bamFolder, normalsample) + '_markdup_BQSR_FIXED.bam',
    ' --normal_panel ' + jp(variantFolder, 'MuTect2_PON.vcf'),' -o ' + jp(variantFolder, tumorsample) + '.vcf'), '>>', logFile, '2>&1'])
    log(cmd, logCommands)
    # can  add --annotation 
    # can add --contamination_fraction_to_filter 
    # can add --standard_min_confidence_threshold_for_calling 30 (default)
    # --output_mode EMIT_VARIANTS_ONLY

    logCommands.close()
