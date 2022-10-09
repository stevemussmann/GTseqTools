# GTseqTools
Program for filtering GTseq genotype data and converting to various file formats

This program is a work in progress. This README.md file will be updated regarding program functionality as features are added.

## Python Version Compatibility
This program has only been tested in Python v3.10. However, it should be compatible with Python v3.8+. Compatibility is somewhat restrictive because the GTconvert class uses syntax that is new to Python as of v3.8.

## Dependencies
- pandas

## Development Notes
- Additional file format conversion options will be implemented.
- Some existing format conversions will be modified or have additional options added.
- Minimal error checking procedures have been implemented.

## Order of operations
The program first conducts all filtering procedures prior to file format conversion. Filtering procedures are conducted in the following order:
1) Remove user-specified individuals (-r option).
2) Remove species-identification loci (-s option).
3) Remove sex-identifying loci (-d option).
4) Remove loci that do not meet the minimum threshold (-l option).
5) Remove individuals that do not meet the minimum threshold (-i option).

## Input Requirements
The minimal input is a Microsoft Excel formatted file (.xlsx). All data should be in a worksheet titled 'Final Genotypes'. The first row should be a header line, with cell A1 specifying the individual sample column, cell B1 should contain the text 'Population ID', and cells C1 to the end should specify locus names. Alleles for a genotype should be concatenated per locus (e.g., AA, AT, etc.). A missing genotype for a locus should be recorded as '0'. Special columns can be included for certain file formats (e.g., SNPPIT; see explanation below in [File Conversion Input Details](#conversion)). Some of the above format options for Excel files will (hopefully) be more flexible / customizable in future versions of this program.

Optionally, you can also provide plain text files with individuals or loci to be stripped from the input file (see -d, -r, and -s options in the [Optional Arguments](#optional) below). Each of these files should contain a single column of data listing a single individual or locus per line.

## Program Options
Required Inputs:
* **-x / --infile:** Specify an input Excel file containing GTseq data. 

Required for SNPPIT conversion only:
* **-Z / --snppitmap:** Specify a tab-delimited map in which the first column lists each population, the second column lists its status as POP or OFFSPRING, and the third column lists the potential parental POP(s) for each OFFSPRING. See example snppitmap in 'example_files' folder. 

Optional Arguments: <a name="optional"></a>
* **-d / --sexid:** Provide a list of loci that are sex-identifying SNPs. This should be a plain text file with one locus per line. These loci will be removed from the dataset before any data filtering steps are executed. 
* **-i / --pmissind:** Enter the maximum allowable proportion of missing data for an individual sample. Default = 0.2.
* **-l / --pmissloc:** Enter the maximum allowable proportion of missing data for a locus. Default = 0.1.
* **-r / --removelist:** Provide a list of individuals that should be removed from the input xlsx file. This should be a plain text file with each individual being specified on its own line. These individuals will be removed before missing data proportions are calculated. 
* **-s / --species:** Provide a list of loci that are species identification SNPs. This should be a plain text file with one locus per line. These loci will be removed from the dataset before any other data filtering steps are executed. 
* **-t / --twoline:** If a Structure file is to be written, use this option to write it in two-line format. Default = single-line Structure format.

Current supported file conversions:
* **-g / --genepop:** Prints a file in genepop format.
* **-n / --newhybrids:** Prints a file in newhybrids format.
* **-p / --plink:** Prints a file in plink format. Result is similar to using the --recode12 option in plink. Output should be valid for the program [Admixture](https://dalexander.github.io/admixture/)
* **-S / --structure:** Prints a file in structure format (default = single line per individual. See '-t' option above).
* **-X / --xlsx:** Writes an xlsx-formatted file after user-specified individuals are removed (-r option) but before any other filtering steps are applied.
* **-z / --snppit:** (under development) Prints a file in snppit format (-Z option is also required for snppit conversion as specified above).

## Outputs
Outputs retain the input file (-x / --infile) base name, but change the output file extension depending upon format. File formats are output with the following file extensions:

| Format       | Extension(s)  | Program Option |
| :----------: | :-----------: | :------------: |
| Excel        | .xlsx         | -X             |
| Genepop      | .gen          | -g             |
| NewHybrids   | .newhyb       | -n             |
| Plink        | .ped and .map | -p             |
| SNPPIT       | .snppit       | -z             |
| Structure    | .str          | -S             |

## Example Commands
You can print the program help menu using the -h option:
```
gtSeqConvert.py -h
```

The command below would convert the data in the Excel format to a pandas dataframe, remove Species-identifying SNPs listed in the 'speciesIdSNPs.txt' file, remove individuals with the proportion of missing data 0.1, then perform a conversion to a Structure format file with data arranged in two lines per individual. 
```
gtSeqConvert.py -x GTseqData.xlsx -i 0.1 -s speciesIdSNPs.txt -S -t
```

All file conversions occur independently of one another, so the following command would also be valid to write genepop, newhybrids, and structure files in a single command:
```
gtSeqConvert.py -x GTseqData.xlsx -i 0.1 -s speciesIdSNPs.txt -S -g -n
```

SNPPIT format requires some extra information to complete the conversion (see explanation below in [File Conversion Input Details](#conversion):
```
gtSeqConvert.py -x GTseqData.xlsx -z -Z snppitmap.txt
```

## File Conversion Input Details <a name="conversion"></a>
### SNPPIT
The SNPPIT conversion has a few special requirements that are not needed for other file formats. Firstly, a special tab-delimited snppit map file is required as supplemental input. An example of the snppit map file is included in the 'example_files' folder. Essentially, each line of this file is intended to contain all of the information of lines starting with the POP and OFFSPRING keywords, as seen on [pages 22-23 of the SNPPIT program documentation](https://github.com/eriqande/snppit/blob/master/doc/snppit_doc.pdf). However, note that the columns of the snppitmap are in a different order than they appear in the final snppit-formatted file (i.e., 'popname'\tab'POP' rather than 'POP'\tab'popname').

Secondly, the user can utilize SNPPIT's 'optional' columns as seen on [pages 24-26 of the SNPPIT program documentation](https://github.com/eriqande/snppit/blob/master/doc/snppit_doc.pdf) by including the relevant data in their input .xlsx file. To do this, add columns to your input .xlsx file with headings that exactly match the optional columns used by SNPPIT. For example, if you want to use the POPCOLUMN_SEX option in SNPPIT, then include a column named exactly POPCOLUMN_SEX in the 'Final Genotypes' worksheet of your input .xlsx file, and fill this column with the appropriate values for each individual, as necessary.

Generally, the values you input in these optional columns should exactly match the values as they would appear in the final SNPPIT file. Additional details are as follows:
* Values in the POPCOLUMN_SEX column are somewhat flexible. Case-insensitive versions of 'f' and 'female' or 'm' and 'male' will be converted to 'F' and 'M' respectively. Blank cells and any other values entered in this column will be converted to missing data ('?').
* Values in columns containing year data (POPCOLUMN_REPRO_YEARS, OFFSPRINGCOLUMN_BORN_YEAR, OFFSPRINGCOLUMN_SAMPLE_YEAR) must be valid four-digit integers.
* Currently there are no data validation measures implemented for the other two optional columns (POPCOLUMN_SPAWN_GROUP and OFFSPRINGCOLUMN_AGE_AT_SAMPLING) so please make sure anything you enter in these columns is exactly as you want it to appear in the final file.
* Unnecessary data can be left as blank cells. An example of this is that you would not need to enter sex data for OFFSPRING groups in the POPCOLUMN_SEX column.
