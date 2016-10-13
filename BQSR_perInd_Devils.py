#!/usr/bin/env python
#import argparse
#from glob import glob

#--s test_samples.txt
#--b /mnt/lfs2/hend6746/devils/reference/sarHar1.fa
#--k /mnt/lfs2/hend6746/taz/filtered_plink_files/export_data_150907

from os.path import join as jp
from os.path import abspath
import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-s', "--samples", help="Samples.txt file with sample ID.", required=True)
parser.add_argument('-b', "--bwaindex", help="Path to bwa index file.", required=True)
parser.add_argument('-k', "--knownsites", help="path and fileName of filteredSNP.vcf.", required=True)
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
PBS_scripts = abspath('GATK_PBS_scripts')
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
    logFile = jp(variantFolder, sample + '_GATK.log')
    logCommands = open(jp(PBS_scripts, sample + '_commands.sh'), 'w')

    #Setup for qsub
    log('#!/bin/bash', logCommands)
    log('#PBS -N %s' % sample, logCommands)
    log('#PBS -j oe', logCommands)
    log('#PBS -o %s_job.log' % sample, logCommands)
    log('#PBS -m abe', logCommands)
    log('#PBS -M shendri4@gmail.com', logCommands)
    log('#PBS -q short', logCommands)
    log('#PBS -l mem=100000', logCommands)
    log(". /usr/modules/init/bash", logCommands)
    log("module load python/2.7.10", logCommands)
    log("module load grc", logCommands)

####################
#	BaseQualityRecalibration
#	Step 1: first run of BQSR: BaseRecalibrator
####################
    cmd = ' '.join([gatkCall, ' -nct 24 ',
    ' -T BaseRecalibrator ',
    + jp(bamFolder, sample) + '.bam',
    ' -knownSites ' knownSites,
    ' -o ' + jp(variantFolder, sample) + '.table', '>>', logFile, '2>&1'])
    log(cmd, logCommands)

####################
#	BaseQualityRecalibration
#	Step 2: BaseRecalibrator on recalibrated files
####################
# 
# for CURRENT_KEY in `cat ${INPUT_DIR}/big_output/bam/${KEY}_addRG_realign_fixMate.list`
# do
# java -Xmx120g -jar /mnt/home/hend6746/modules/GenomeAnalysisTK-2.6-4-g3e5ff60/GenomeAnalysisTK.jar \
# 	-nct 24 \
# 	-T BaseRecalibrator \
# 	-I ${WORK_DIR}/${CURRENT_KEY} \
# 	-R ${PROJ_DIR}/reference/canfam31/canfam31.fa \
# 	-knownSites ${PROJ_DIR}/vcf/union_variants_max100000_min2var_variants.vcf \
# 	-BQSR recal_data_${CURRENT_KEY}_min2var_FIXED.table \
# 	-o post_recal_data_${CURRENT_KEY}_min2var_FIXED.table \
# 	--intervals ${PROJ_DIR}/bed_files/baits_canfam3.1_sorted_merged.bed \
# 	--interval_padding 1000
# done
# 
# ####################
# #	BaseQualityRecalibration
# #	Step 3: PrintReads
# # 	Apply recalibration table to original bam file
# ####################
# 
# for CURRENT_KEY in `cat ${INPUT_DIR}/big_output/bam/${KEY}_addRG_realign_fixMate.list`
# do
# java -Xmx120g -jar /mnt/home/hend6746/modules/GenomeAnalysisTK-2.6-4-g3e5ff60/GenomeAnalysisTK.jar \
# 	-nct 24 \
#     -T PrintReads \
# 	-I ${WORK_DIR}/${CURRENT_KEY} \
#     -R ${PROJ_DIR}/reference/canfam31/canfam31.fa \
#     -BQSR recal_data_${CURRENT_KEY}_min2var_FIXED.table \
# 	-o recal_${CURRENT_KEY}_min2var_FIXED.bam \
# 	--intervals ${PROJ_DIR}/bed_files/baits_canfam3.1_sorted_merged.bed \
# 	--interval_padding 1000
# done
# exit 0;
    
    logCommands.close()
