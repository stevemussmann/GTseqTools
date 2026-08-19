# Example Files

This directory contains example files to help with properly formatting inputs and testing the features of GTseqTools.

## Files
This directory contains the following files:
* **`exampleData.xlsx`**: This is the example genotype data file. It contains extra data columns for Colony2, NewHybrids, Sequoia, and SNPPIT data file conversions. 
* **`markerErrorRates.txt`**: This file contains locus-specific genotype error rates that can be applied to the Colony2 output format. 
* **`sexID.txt`**: This is an example file for listing sex ID markers to be removed from the genotype file. Similar formats are used for processes such as removing species ID markers, unwanted individual samples, and other purposes. 
* **`snppitMap.txt`**: This is a SNPPIT map file that is required for the SNPPIT conversion. 

**All files in the `example_files` directory contain 'dummy' data that were generated and modified solely for the purpose of testing and validating outputs of GTseqTools.**

## Example Processing
The bash script in the code block below shows an example of how to process the example data file in this directory.

```
#!/bin/bash

source ~/miniconda3/etc/profile.d/conda.sh
conda activate GTseqTools

FILE="exampleData.xlsx"
SEX="sexID.txt"
SNPPIT="snppitMap.txt"
ERR="markerErrorRates.txt"

gtSeqConvert.py -x $FILE -d $SEX -Z $SNPPIT -f $ERR \
	-m -l 0.1 -i 0.2 -o "individuals" -D -k "first" \
	-M 0.6 -F 0.6 -y 1 -Y 1 -N "exampleDataTestRun" \
	--genepop --newhybrids --snppit --sequoia --colony

exit
```

This command uses a set of options that will perform several different operations. I split the command across multiple lines, and grouped similar-purpose commands on each line. This formatting is optional, but I prefer it because I find that it makes long commands more readable.
The options on the first line read in various input files:
* `-x $FILE`: Read in in the genotype file
* `-d $SEX`: Read the text file containing the list of sex identifying markers
* `-Z $SNPPIT`: Read the SNPPIT map file
* `-f $ERR`: Read the file of locus-specific genotyping error rates (used in the Colony format)

The second line is used to apply various filtering options:
* `-m`: Apply the monomorphic locus filter
* `-l 0.1`: Remove loci with >10% missing data
* `-i 0.2`: Remove individuals with >20% missing data
* `-o "individuals"`: This option will cause the `-i` filter to be applied before the `-l` filter
* `-D`: Screen the input file for duplicate genotypes
* `-k "first"`: Retain the first individual encountered from any pairs of duplicates

The third line contains commands used by the Colony2 format:
* `-M 0.6`: Sets the probability of a father being among the candidate parents to 0.6
* `-F 0.6`: Sets the probability of a mother being among the candidate parents to 0.6
* `-y 1`: Turns on monogamy for males
* `-Y 1`: Turns on monogamy for females
* `-N "exampleDataTestRun"`: This applies the run name `exampleDataTestRun` to the Colony2 format. When the input file is run in Colony2, all outputs will start with `exampleDataTestRun`.

The fourth line lists the various output formats I have requested:
* `--colony`: Output a file in Colony2 format
* `--genepop`: Output a file in Genepop format
* `--newhybrids`: Output a file in NewHybrids format
* `--snppit`: Output a file in SNPPIT format
* `--sequoia`: Output a file in Sequoia format

