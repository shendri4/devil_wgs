


    #Number of raw reads
grep "Total pairs:"' + jp(rawdataDir, sample + ), '>>', jp(resultsDir, sample + 'qualityStats_output.txt'), '>>', logFile, '2>&1'])

zcat test_165499_cleaned_PE1.fastq.gz | echo $((`wc -l`/4))

