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

###########################################################################
#### Extract the Indels from the call set
cmd = ' '.join([gatkCall, ' -T SelectVariants ', 
' -o ' + jp(variantFolder, variant + '_raw_indels.vcf'), 
' -V ' + jp(variantFolder, variant + '.vcf'), 
' -selectType INDEL ',
'>>', logFile, '2>&1'])
log(cmd, logCommands)

###########################################################################
#### Apply the filter to the Indel call set
cmd = ' '.join([gatkCall, ' -T VariantFiltration ', 
' -V ' + jp(variantFolder, variant + '_raw_indels.vcf'), 
' -o ' + jp(variantFolder, variant + '_filtered_indels.vcf'), 
' --filterExpression "QD < 2.0 || FS > 200.0 || ReadPosRankSum < -20.0" ', 
' --filterName "Badindel" ',
'>>', logFile, '2>&1'])
log(cmd, logCommands)   
    
    --filterName "BadIndel-QD" \
	--filterExpression "vc.getType().toString().equals('INDEL') && (QD < 2.0)" \
	--filterName "BadIndel-ReadPosRankSum" \
	--filterExpression "vc.getType().toString().equals('INDEL') && (ReadPosRankSum < -20.0)" \
	--filterName "BadIndel-FS" \
	--filterExpression "vc.getType().toString().equals('INDEL') && (FS > 200.0)" \
	--filterName "BadIndel-SOR" \
	--filterExpression "vc.getType().toString().equals('INDEL') && (SOR > 10.0)" \
	#The InbreedingCoeff statistic is a population-level calculation that is only available with 10 or more samples. 
	#If you have fewer samples you will need to omit that particular filter statement.
	#--filterName "BadIndel-InbreedingCoeff" \
	#--filterExpression "vc.getType().toString().equals('INDEL') && (InbreedingCoeff < -0.8)"

###########################################################################
#### Exclude non-variant loci and filtered loci (trim remaining alleles by default):
cmd = ' '.join([gatkCall, ' -T SelectVariants ', 
' -o ' + jp(variantFolder, variant + '_selected_filtered_indels.vcf'), 
' -V ' + jp(variantFolder, variant + '_filtered_indels.vcf'), 
' --excludeNonVariants ', ' --excludeFiltered ',
'>>', logFile, '2>&1'])
log(cmd, logCommands)
   	
###########################################################################
################################## 
## Evaluate all variants in file 
################################## 
cmd = ' '.join([gatkCall, ' -T VariantEval ', 
' -o ' + jp(variantResults, variant + '_selected_filtered_indels.eval.gatkreport.grp'), 
' --eval: ' + jp(variantFolder, variant + '_selected_filtered_indels.vcf'), 
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