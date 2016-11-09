#!/usr/bin/env python
#import argparse
#from glob import glob

from os.path import join as jp
from os.path import abspath
import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-s', "--variant", help="raw variant (.vcf) file", required=True)
parser.add_argument('-b', "--bwaindex", help="Path to bwa index file.", required=True)
args = parser.parse_args()

VERBOSE=False

#Function definitions:
def log(txt, out):
    if VERBOSE:
        print(txt)
    out.write(txt+'\n')
    out.flush()

# Setup folders and paths variables:
variantFolder = abspath('03-Calls')
variantResults = abspath('03-Calls/qc')
PBS_scripts = abspath('MuTect_PBS_scripts')
normal_PBS_scripts = abspath('MuTect_PBS_scripts/normal_PBS_scripts')
tumor_PBS_scripts = abspath('MuTect_PBS_scripts/tumor_PBS_scripts')
bwaIndex = abspath(args.bwaindex)
gatkCall = 'java -jar /opt/modules/biology/gatk/3.5/bin/GenomeAnalysisTK.jar -R %s' % bwaIndex

os.system('mkdir -p %s' % bamFolder)
os.system('mkdir -p %s' % variantFolder)
os.system('mkdir -p %s' % PBS_scripts)
os.system('mkdir -p %s' % normal_PBS_scripts)
os.system('mkdir -p %s' % tumor_PBS_scripts)

##### Run pipeline ###
# for normalsample in normalsamples:
#     print "Processing", normalsample, "....."

# Set up files:
logFile = jp(variantFolder, 'GATK_filter.log')
logCommands = open(jp(normal_PBS_scripts,'GATK_filter_commands.sh'), 'w')

#Setup for qsub
log('#!/bin/bash', logCommands)
log('#PBS -N filter', logCommands)
log('#PBS -j oe', logCommands)
log('#PBS -o filter_job.log', logCommands)
log('#PBS -m abe', logCommands)
log('#PBS -M shendri4@gmail.com', logCommands)
log('#PBS -q short', logCommands)
log('#PBS -l mem=100gb', logCommands)
log(". /usr/modules/init/bash", logCommands)
log("module load python/2.7.10", logCommands)
log("module load grc", logCommands)

################################## 
## Evaluate all raw variants in file to see quality of variants before filters are applied (OPTIONAL)
################################## 
cmd = ' '.join([gatkCall, ' -T VariantEval ', 
' -o ' + jp(variantResults, variant + 'variants.raw.eval.gatkreport.grp'), 
' --eval: ' + jp(variantFolder, variant + '.vcf'), 
' --doNotUseAllStandardStratifications ', ' --doNotUseAllStandardModules ', ' --evalModule CountVariants ',
'>>', logFile, '2>&1'])
log(cmd, logCommands)

###########################################################################
#### Extract the SNPs from the call set
cmd = ' '.join([gatkCall, ' -T SelectVariants ', 
' -o ' + jp(variantFolder, variant + '_raw_SNPs.vcf'), 
' -V ' + jp(variantFolder, variant + '.vcf'), 
' -selectType SNP ',
'>>', logFile, '2>&1'])
log(cmd, logCommands)
    
###########################################################################
#### High quality filters
#### Filter variant sites from raw variants
cmd = ' '.join([gatkCall, ' -T VariantFiltration ', 
' -V ' + jp(variantFolder, variant + '_raw_SNPs.vcf'), 
' -o ' + jp(variantFolder, variant + '_filtered_SNPs.vcf'), 
' --filterExpression "QD < 2.0 || FS > 60.0 || MQ < 40.0 || MQRankSum < -12.5 || ReadPosRankSum < -8.0" ', 
' --filterName "BadSNP" ',
'>>', logFile, '2>&1'])
log(cmd, logCommands)

	--variant:VCF ${PROJ_DIR}/nonfiltered_allsites_93ind.recode.vcf \
	--filterName "BadSNP-QD"  \
	--filterExpression "(vc.getType().toString().equals('SNP') || vc.getType().toString().equals('MNP')) && (QD < 2.0)" \
	--filterName "BadSNP-MQ" \
	--filterExpression "(vc.getType().toString().equals('SNP') || vc.getType().toString().equals('MNP')) && (MQ < 40.0)" \
	--filterName "BadSNP-SOR" \
	--filterExpression "(vc.getType().toString().equals('SNP') || vc.getType().toString().equals('MNP')) && (SOR > 3.0)" \
	--filterName "BadSNP-FS" \
	--filterExpression "(vc.getType().toString().equals('SNP') || vc.getType().toString().equals('MNP')) && (FS > 60)" \
	--filterName "BadSNP-MQRankSum" \
	--filterExpression "(vc.getType().toString().equals('SNP') || vc.getType().toString().equals('MNP')) && (MQRankSum < -12.5)" \
	--filterName "BadSNP-ReadPosRankSum" \
	--filterExpression "(vc.getType().toString().equals('SNP') || vc.getType().toString().equals('MNP')) && (ReadPosRankSum < -8.0)" \

#### GQ20
cmd = ' '.join([gatkCall, ' -T VariantFiltration ', 
' -o ' + jp(variantFolder, variant + '_GQ20_filtered_SNPs.vcf'), 
' -V ' + jp(variantFolder, variant + '_filtered_SNPs.vcf'), 
' G_filter "GQ < 20.0" ',
' G_filterName lowGQ ',
'>>', logFile, '2>&1'])
log(cmd, logCommands)

# the DP threshold should be set a 5 or 6 sigma from the mean coverage across all samples, 
# so that the DP > X threshold eliminates sites with excessive coverage caused by alignment artifacts.

###########################################################################
#### Exclude non-variant loci and filtered loci (trim remaining alleles by default):
cmd = ' '.join([gatkCall, ' -T SelectVariants ', 
' -o ' + jp(variantFolder, variant + '_selected_GQ20_filtered_SNPs.vcf'), 
' -V ' + jp(variantFolder, variant + '_GQ20_filtered_SNPs.vcf'), 
' --excludeNonVariants ', ' --excludeFiltered ',
'>>', logFile, '2>&1'])
log(cmd, logCommands)
   	
###########################################################################
################################## 
## Evaluate all variants in file 
################################## 
cmd = ' '.join([gatkCall, ' -T VariantEval ', 
' -o ' + jp(variantResults, variant + '_selected_GQ20_filtered_SNPs.eval.gatkreport.grp'), 
' --eval: ' + jp(variantFolder, variant + '_selected_GQ20_filtered_SNPs.vcf'), 
' --doNotUseAllStandardStratifications ', ' --doNotUseAllStandardModules ',
' --evalModule CountVariants '
' --evalModule TiTvVariantEvaluator '
' --stratificationModule CompRod '
' --stratificationModule EvalRod '
' --stratificationModule Sample '
' --stratificationModule Filter '
' --stratificationModule FunctionalClass '
'>>', logFile, '2>&1'])
log(cmd, logCommands)
		
logCommands.close()
	
