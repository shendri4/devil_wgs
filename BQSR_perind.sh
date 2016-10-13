# commands used November 2013 by RMS
# modified commands used November 2015 by SAH
#./SH_Step7_BQSR_perind_scratch.sh 150913_HS3AB HS3B_Wayne RKWSH002 L002
####################
#	 BASIC INFO
####################
## user-defined variables ###
RUN_DATE=$1
RUN_ID=$2
LIB_NAME=$3
LANE_NUMBER=$4
KEY=${LIB_NAME}_${LANE_NUMBER}

## where the data will be 
PROJ_DIR="/mnt/home/hend6746/scratch/wolves"
INPUT_DIR=${PROJ_DIR}/fastq/${RUN_DATE}/${RUN_ID}
## where big files go
BIG_OUTPUT_DIR=$INPUT_DIR/big_output/
WORK_DIR=$BIG_OUTPUT_DIR/bam/
PERIND_OUTPUT_DIR=$BIG_OUTPUT_DIR/perind_recal/
mkdir -p ${PERIND_OUTPUT_DIR}
## where my analysis goes

####################
#	BaseQualityRecalibration
#	using 'known' vcf
####################
#need to do this in each directory 
#ls ${INPUT_DIR}/big_output/bam/${LIB_NAME}_S*_${LANE_NUMBER}_addRG_realign_fixMate.bam > ${KEY}_addRG_realign_fixMate.list

####################
#	BaseQualityRecalibration
#	Step 1: BaseRecalibrator
####################
source /usr/modules/init/bash
#module load gatk

cd ${PERIND_OUTPUT_DIR}

## first run of BQSR: BaseRecalibrator
for CURRENT_KEY in `cat ${INPUT_DIR}/big_output/bam/${KEY}_addRG_realign_fixMate.list`
do
java -Xmx120g -jar /mnt/home/hend6746/modules/GenomeAnalysisTK-2.6-4-g3e5ff60/GenomeAnalysisTK.jar \
	-nct 24 \
	-T BaseRecalibrator \
	-I ${WORK_DIR}/${CURRENT_KEY} \
	-R ${PROJ_DIR}/reference/canfam31/canfam31.fa \
	-knownSites ${PROJ_DIR}/vcf/union_variants_max100000_min2var_variants.vcf \
	-o recal_data_${CURRENT_KEY}_min2var_FIXED.table \
	--intervals ${PROJ_DIR}/bed_files/baits_canfam3.1_sorted_merged.bed \
	--interval_padding 500 
done

####################
#	BaseQualityRecalibration
#	Step 2: BaseRecalibrator on recalibrated files
####################

for CURRENT_KEY in `cat ${INPUT_DIR}/big_output/bam/${KEY}_addRG_realign_fixMate.list`
do
java -Xmx120g -jar /mnt/home/hend6746/modules/GenomeAnalysisTK-2.6-4-g3e5ff60/GenomeAnalysisTK.jar \
	-nct 24 \
	-T BaseRecalibrator \
	-I ${WORK_DIR}/${CURRENT_KEY} \
	-R ${PROJ_DIR}/reference/canfam31/canfam31.fa \
	-knownSites ${PROJ_DIR}/vcf/union_variants_max100000_min2var_variants.vcf \
	-BQSR recal_data_${CURRENT_KEY}_min2var_FIXED.table \
	-o post_recal_data_${CURRENT_KEY}_min2var_FIXED.table \
	--intervals ${PROJ_DIR}/bed_files/baits_canfam3.1_sorted_merged.bed \
	--interval_padding 1000
done

####################
#	BaseQualityRecalibration
#	Step 3: PrintReads
# 	Apply recalibration table to original bam file
####################

for CURRENT_KEY in `cat ${INPUT_DIR}/big_output/bam/${KEY}_addRG_realign_fixMate.list`
do
java -Xmx120g -jar /mnt/home/hend6746/modules/GenomeAnalysisTK-2.6-4-g3e5ff60/GenomeAnalysisTK.jar \
	-nct 24 \
    -T PrintReads \
	-I ${WORK_DIR}/${CURRENT_KEY} \
    -R ${PROJ_DIR}/reference/canfam31/canfam31.fa \
    -BQSR recal_data_${CURRENT_KEY}_min2var_FIXED.table \
	-o recal_${CURRENT_KEY}_min2var_FIXED.bam \
	--intervals ${PROJ_DIR}/bed_files/baits_canfam3.1_sorted_merged.bed \
	--interval_padding 1000
done
exit 0;


