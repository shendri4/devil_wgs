#!/usr/bin/env python
#import argparse
#from glob import glob

#-s test_samples.txt
#-b /mnt/lfs2/hend6746/devils/reference/sarHar1.fa
#-k /mnt/lfs2/hend6746/taz/filtered_plink_files/export_data_150907/seventy.1-2.nodoubletons.noparalogs.noX.plink.oneperlocus.vcf

from os.path import join as jp
from os.path import abspath
import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-s', "--samples", help="Samples.txt file with sample ID.", required=True)
parser.add_argument('-b', "--bwaindex", help="Path to bwa index file.", required=True)
parser.add_argument('-k', "--knownsites", help="Path and fileName of filteredSNP.vcf.", required=True)
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
samples = []
for l in open(args.samples):
    if len(l) > 1:
        samples.append(l.split('/')[-1].replace('.fastq.1.gz', '').strip())

# Setup folders and paths variables:
bamFolder = abspath('02-Mapped')
variantFolder = abspath('03-Calls')
PBS_scripts = abspath('BQSR_PBS_scripts')
#rawdataDir = abspath(args.rawdata)
bwaIndex = abspath(args.bwaindex)
knownSites = abspath(args.knownsites)
gatkCall = 'java -jar /opt/modules/biology/gatk/3.5/bin/GenomeAnalysisTK.jar -R %s' % bwaIndex

os.system('mkdir -p %s' % bamFolder)
os.system('mkdir -p %s' % variantFolder)
os.system('mkdir -p %s' % PBS_scripts)

##### Run pipeline ###
for sample in samples:
    print "Processing", sample, "....."
    # Set up files:
    logFile = jp(bamFolder, sample + '_BQSR.log')
    logCommands = open(jp(PBS_scripts, sample + '_BQSR_commands.sh'), 'w')

    #Setup for qsub
    log('#!/bin/bash', logCommands)
    log('#PBS -N %s' % sample, logCommands)
    log('#PBS -j oe', logCommands)
    log('#PBS -o %s_job.log' % sample, logCommands)
    log('#PBS -m abe', logCommands)
    log('#PBS -M shendri4@gmail.com', logCommands)
    log('#PBS -q short', logCommands)
    log('#PBS -l mem=100gb', logCommands)
    log(". /usr/modules/init/bash", logCommands)
    log("module load python/2.7.10", logCommands)
    log("module load grc", logCommands)

####################
#	BaseQualityRecalibration
#	Step 1: First run of BQSR: BaseRecalibrator
####################
    cmd = ' '.join([gatkCall, ' -nct 24 ', ' -T BaseRecalibrator ', ' -I ' + jp(bamFolder, sample) + '.bam', ' -knownSites ' + knownSites,
    ' -o ' + jp(bamFolder, sample) + '_BQSR.table', '>>', logFile, '2>&1'])
    log(cmd, logCommands)

####################
#	BaseQualityRecalibration
#	Step 2: BaseRecalibrator on recalibrated files
####################

    cmd = ' '.join([gatkCall, ' -nct 24 ',
    ' -T BaseRecalibrator ',
    ' -I ' + jp(bamFolder, sample) + '.bam',
    ' -knownSites ' + knownSites,
    ' -BQSR ' + jp(bamFolder, sample) + '_BQSR.table'
    ' -o ' + jp(bamFolder, sample) + '_BQSR_FIXED.table', '>>', logFile, '2>&1'])
    log(cmd, logCommands)

####################
#	BaseQualityRecalibration
#	Step 3: PrintReads
#	Apply recalibration table to original bam file
####################

    cmd = ' '.join([gatkCall, ' -nct 24 ',
    ' -T PrintReads ',
    ' -I ' + jp(bamFolder, sample) + '.bam',
    ' -knownSites ' + knownSites,
    ' -BQSR ' + jp(bamFolder, sample) + '_BQSR_FIXED.table'
    ' -o ' + jp(bamFolder, sample) + '_BQSR_FIXED.bam', '>>', logFile, '2>&1'])
    log(cmd, logCommands)

    logCommands.close()
