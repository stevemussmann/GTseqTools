# Example Files

This directory contains example files to help with properly formatting inputs and testing the features of GTseqTools.

## Files
This directory contains the following files:
* **`exampleData.xlsx`**: This is the example genotype data file. It contains extra data columns for NewHybrids, Sequoia, and SNPPIT data file conversions. 
* **`sexID.txt`**: This is an example file for listing sex ID markers to be removed from the genotype file. Similar formats are used for processes such as removing species ID markers, unwanted individual samples, and other purposes. 
* **`snppitMap.txt`**: This is a SNPPIT map file that is required for the SNPPIT conversion. 


## Example Processing
The bash script in the code block below shows an example of how to process the example data file in this directory.

```
#!/bin/bash

source ~/miniconda3/etc/profile.d/conda.sh
conda activate GTseqTools

FILE="exampleData.xlsx"
SEX="sexID.txt"
SNPPIT="snppitMap.txt"

gtSeqConvert.py -x $FILE -d $SEX -Z $SNPPIT \
	-m -l 0.1 -i 0.2 -o "individuals" -D \
	--colony --genepop --newhybrids --snppit --sequoia

exit
```

This set of options will perform the following operations:
* `-x $FILE`: Read in in the genotype file
* `-d $SEX`: Read the text file containing the list of sex identifying markers
* `-Z $SNPPIT`: Read the SNPPIT map file
* `-m`: Apply the monomorphic locus filter
* `-l 0.1`: Remove loci with >10% missing data
* `-i 0.2`: Remove individuals with >20% missing data
* `-o "individuals"`: This option will cause the `-i` filter to be applied before the `-l` filter
* `-D`: Screen the input file for duplicate genotypes
* `--colony`: Output a file in Colony2 format
* `--genepop`: Output a file in Genepop format
* `--newhybrids`: Output a file in NewHybrids format
* `--snppit`: Output a file in SNPPIT format
* `--sequoia`: Output a file in Sequoia format
