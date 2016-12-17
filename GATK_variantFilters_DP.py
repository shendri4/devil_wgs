#!/usr/bin/env python
#import argparse
#from glob import glob

from os.path import join as jp
from os.path import abspath
import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-s', "--variants", help="List of joint (raw) variant (.vcf) files", required=True)
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
variants = []
for l in open(args.variants):
    if len(l) > 1:
        variants.append(l.split('/')[-1].replace('.vcf', '').strip())
print variants

# Setup folders and paths variables:
bamFolder = abspath('02-Mapped')
variantFolder = abspath('03-Calls')
jointFolder = abspath('04-Joint_Calls')
filteredFolder = abspath('05-Filtered_Calls')
PBS_scripts = abspath('filter_GATK_PBS_scripts')
bwaIndex = abspath(args.bwaindex)
gatkCall = 'java -jar /opt/modules/biology/gatk/3.5/bin/GenomeAnalysisTK.jar -R %s' % bwaIndex

os.system('mkdir -p %s' % bamFolder)
os.system('mkdir -p %s' % variantFolder)
os.system('mkdir -p %s' % jointFolder)
os.system('mkdir -p %s' % filteredFolder)
os.system('mkdir -p %s' % PBS_scripts)

##### Run pipeline ###
for variant in variants:
	print "Processing", variant, "....."
	# Set up files:
	logFile = jp(filteredFolder, variant + '_GATK_DP_filter.log')
	logCommands = open(jp(PBS_scripts, variant + '_GATK_DP_filter_commands.sh'), 'w')

	#Setup for qsub
	log('#!/bin/bash', logCommands)
	log('#PBS -N %s_filter' % variant, logCommands)
	log('#PBS -j oe', logCommands)
	log('#PBS -o %s_filter_job.log' % variant, logCommands)
	log('#PBS -m abe', logCommands)
	log('#PBS -M shendri4@gmail.com', logCommands)
	log('#PBS -q reg', logCommands)
	log('#PBS -l mem=100gb', logCommands)
	log(". /usr/modules/init/bash", logCommands)
	log("module load python/2.7.10", logCommands)
	log("module load grc", logCommands)

	###########################################################################
	#### High quality filters
	#### Filter variant sites from raw variants
	cmd = ' '.join([gatkCall, ' -T VariantFiltration ', 
	' -V ' + jp(jointFolder, variant + '_selected_GQ20_filtered_SNPs.vcf'), 
	' -o ' + jp(filteredFolder, variant + '_minDP10_maxDP150_GQ20_filtered_SNPs.vcf'), 
	' --filterExpression "DP < 10.0" ', 
	' --filterName "BadSNP" ',
	'>>', logFile, '2>&1'])
	log(cmd, logCommands)


	# the DP threshold should be set a 5 or 6 sigma from the mean coverage across all samples, 
	# so that the DP > X threshold eliminates sites with excessive coverage caused by alignment artifacts.

	###########################################################################
	#### Exclude non-variant loci and filtered loci (trim remaining alleles by default):
	cmd = ' '.join([gatkCall, ' -T SelectVariants ', 
	' -o ' + jp(filteredFolder, variant + '_selected_minDP10_maxDP150_GQ20_filtered_SNPs.vcf'), 
	'  -V ' + jp(filteredFolder, variant + '_minDP10_maxDP150_GQ20_filtered_SNPs.vcf'), 
	' --excludeNonVariants', ' --excludeFiltered',
	'>>', logFile, '2>&1'])
	log(cmd, logCommands)
	logCommands.close()