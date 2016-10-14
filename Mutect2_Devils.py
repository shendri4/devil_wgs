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
#Normal-only calling for panel of normals (PON) creation
    cmd = ' '.join([gatkCall, ' -nct 24 ', ' -T MuTect2 ', ' -I:normal ' + jp(bamFolder, sample) + '.bam',
    ' --dbsnp ' + knownSites, '  --artifact_detection_mode ', ' -o ' + jp(variantFolder, sample) +  '.vcf', '>>', logFile, '2>&1'])
    log(cmd, logCommands)
    
    #-I:tumor normal1.bam
    #-o output.normal1.vcf

####################
#Create list of all normal samples
variants = []
for sample in samples:
    sample = ' '.join(['-V ' + jp(variantFolder, sample) + '.vcf'])
    variants.append(sample)
        #variants.append(l.join(['--variant ' + jp(variantFolder, sample) + '.raw.snps.indels.g.vcf'].strip('/n').split('\t'))
#print variants
variantList = ' '.join(str(x) for x in variants)
print variantList

####################
#For full PON creation, call each of your normals separately in artifact detection mode. Then use CombineVariants to output only sites where a variant was seen in at least two samples:
    cmd = ' '.join([gatkCall, ' -nct 24 ', ' -T CombineVariants ', variantList, ' -minN 2 ',
    ' --setKey "null" ', ' --filteredAreUncalled ', ' --filteredrecordsmergetype KEEP_IF_ANY_UNFILTERED ', 
    ' -o ' + jp(variantFolder) +  'MuTect2_PON.vcf', '>>', logFile, '2>&1'])
    log(cmd, logCommands)


#      -V output.normal1.vcf -V output.normal2.vcf [-V output.normal2.vcf ...] \
#      -minN 2 \
#      --setKey "null" \
#      --filteredAreUncalled \
#      --filteredrecordsmergetype KEEP_IF_ANY_UNFILTERED \

####################
#Tumor/Normal variant calling
#NEED TO FIGURE OUT HOW TO CREATE LIST OF TUMOR/NORMAL SAMPLES
#     cmd = ' '.join([gatkCall, ' -nct 24 ', ' -T MuTect2 ', ' -I:tumor ' + jp(bamFolder, sample) + '.bam', ' -I:normal ' + jp(bamFolder, sample) + '.bam',
#     ' --normal_panel ' + variantFolder + ' MuTect2_PON.vcf',' -o ' + variantFolder + 'output.vcf', '>>', logFile, '2>&1'])
#     log(cmd, logCommands)
# can  add --annotation 
# can add --contamination_fraction_to_filter 
# can add --standard_min_confidence_threshold_for_calling 30 (default)
# --output_mode EMIT_VARIANTS_ONLY
    logCommands.close()
