# GTseqTools
Program for filtering GTseq genotype data and converting to various file formats

This program is a work in progress. This README.md file will be updated regarding program functionality as features are added.

## Python Version Compatibility
This program has only been tested in Python v3.10. However, it should be compatible with Python v3.8+. Compatibility is somewhat restrictive because the GTconvert class uses syntax that is new to Python as of v3.8.

## Dependencies
- pandas

## Development Notes
- Currently the program is only writing output to stdout rather than output files. 
- Some file format conversion options are not yet fully implemented.
- Minimal error checking procedures have been implemented.

## Order of operations
The program first conducts all filtering procedures prior to file format conversion. Filtering procedures are conducted in the following order:
1) Remove species-identification loci (-s option).
2) Remove sex-identifying loci (functionality not yet enabled).
3) Remove loci that do not meet the minimum threshold (-i option).
4) Remove individuals that do not meet the minimum threshold (-l option).

## Program Options
Required Inputs:
* **-x / --xlsx:** Specify an Excel file containing GTseq data. The first row should be a header line, with cell A1 specifying the individual sample column, cell B1 should contain the text 'Population ID', and cells C1 to the end should specify locus names. These data should all be in a worksheet titled 'Final Genotypes'. Alleles for a genotype should be concatenated per locus (e.g., AA, AT, etc.). A missing genotype for a locus should be recorded as '0'. Some of the format options will (hopefully) be more flexible / customizable in future versions of this program. 

Optional arguments:
* **-i / --pmissind:** Enter the maximum allowable proportion of missing data for an individual sample. Default = 0.2.
* **-l / --pmissloc:** Enter the maximum allowable proportion of missing data for a locus. Default = 0.1.
* **-s / --species:** Provide a list of loci that are species identification SNPs. This should be a plain text file with one locus per line. These loci will be removed from the dataset before any data filtering steps are executed. 
* **-t / --twoline:** If a Structure file is to be written, use this option to write it in two-line format. Default = single-line Structure format.

Current supported file conversions:
* **-g / --genepop:** Prints a file in genepop format.
* **-n / --newhybrids:** Prints a file in newhybrids format.
* **-S / --structure:** Prints a file in structure format (default = single line per individual. See '-t' option above). 
