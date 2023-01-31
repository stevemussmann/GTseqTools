# GTseqTools
Program for filtering GTseq genotype data and converting to various file formats

This program is a work in progress. This README.md file will be updated regarding program functionality as features are added.

## Python Version Compatibility
This program has only been tested in Python v3.10. However, it should be compatible with Python v3.8+. Compatibility is somewhat restrictive because the GTconvert class uses syntax that is new to Python as of v3.8.

## Dependencies
- pandas

## Installation
One option for installation is the setup of a conda environment. This can be accomplished by first installing [Miniconda](https://docs.conda.io/en/latest/miniconda.html), and might be the easiest option if you do not have admin privileges on your computer. Once conda is setup, configure it so that the base environment does not automatically load on startup.
```
conda config --set auto_activate_base false
```

Next, create a conda environment in which this program can be run. Use the following command, which should install a sufficiently recent version of python:
```
conda create -n GTseqTools -c conda-forge python=3 pandas openpyxl
```
The environment can be activated and deactivated as needed with the following commands:
```
conda activate GTseqTools
conda deactivate
```

Next, download this package to the location of your choice with the following command.
```
git clone https://github.com/stevemussmann/GTseqTools.git
```

If necessary, make the software executable:
```
chmod u+x gtSeqConvert.py
```

Finally, put the software in your $PATH. There are many ways of accomplishing this. For example. add the following line (with correct path) to your .bashrc and reload your .bashrc:
```
export PATH=/path/to/GTseqTools:$PATH
```

## Development Notes
- Additional file format conversion options will be implemented.
- Some existing format conversions will be modified or have additional options added.
- Minimal error checking procedures have been implemented. Additional error checking is added with most updates, but some functions have more error checking than others. Please report bugs via the 'issues' menu above. If possible, please attach a copy of an input file that causes the error and include the command used for conversion that caused the error. 

## Order of operations
The program first conducts all filtering procedures prior to file format conversion. Filtering procedures are conducted in the following order:
1) Remove user-specified individuals (-r option).
2) Remove all individuals not belonging to retained populations (-P option).
3) Remove unwanted locus list (-R option).
4) Remove species-identification loci (-s option).
5) Remove sex-identifying loci (-d option).
6) Remove loci that do not meet the minimum threshold (-l option).
7) Remove individuals that do not meet the minimum threshold (-i option).
8) Remove monomorphic loci (-m option).

## Input Requirements
### Required
The minimal input is a Microsoft Excel formatted file (.xlsx). All data should be in a worksheet titled 'Final Genotypes'. The first row should be a header line, with cell A1 specifying the individual sample column, cell B1 should contain the text 'Population ID', and cells C1 to the end should specify locus names. Alleles for a genotype should be concatenated per locus (e.g., AA, AT, etc.). A missing genotype for a locus should be recorded as '0'. Special columns can be included for certain file formats (e.g., SNPPIT; see explanation below in [File Conversion Input Details](#conversion)). Some of the above format options for Excel files will (hopefully) be more flexible / customizable in future versions of this program.

If you are using the GTscore pipeline for genotyping, I have [forked a copy of this repository](https://github.com/stevemussmann/GTscore) and included my [transposeDataGTscore.pl](https://github.com/stevemussmann/GTscore/blob/master/transposeDataGTscore.pl) script which will mostly transform the GTscore genotype outputs to a format compatible with this conversion program. Just open the output of transposeDataGTscore.pl in Microsoft Excel, make sure the worksheet is titled 'Final Genotypes', add the 'Population ID' column, and save the file in .xlsx format.

### Optional
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
* **-m / --monomorphic:** Turn on filter to remove monomorphic loci.
* **-r / --removeinds:** Provide a list of individuals that should be removed from the input xlsx file. This should be a plain text file with each individual being specified on its own line. These individuals will be removed before missing data proportions are calculated. 
* **-P / --keeppops:** Provide a list of populations that will be retained in final outputs. All individuals belonging to populations not specified in this file will be filtered. This input should be a plain text file with each population being specified on its own line. Population names must match those in the 'Population ID' column exactly.
* **-R / --removeloci:** Provide a list of loci that should be removed from the input xlsx file. This should be a plain text file with each locus being specified on its own line. These loci will be removed before any other locus-filtering operations are performed. 
* **-s / --species:** Provide a list of loci that are species identification SNPs. This should be a plain text file with one locus per line. These loci will be removed from the dataset before any other data filtering steps are executed. 

Structure Format Arguments:
* **-H / --header:** Turn off printing of header line with locus names for Structure output
* **-t / --twoline:** Use this option to write structure files in two-line format. Default = single-line Structure format.

Current supported file conversions:
* **-b / --binary:** Prints a file in binary format (0 = major allele, 1 = minor allele, 2 = missing data).
* **-g / --genepop:** Prints a file in genepop format.
* **-n / --newhybrids:** Prints a file in newhybrids format.
* **-p / --plink:** Prints a file in plink format. Result is similar to using the --recode12 option in plink. Output should be valid for the program [Admixture](https://dalexander.github.io/admixture/)
* **-S / --structure:** Prints a file in structure format (default = single line per individual. See '-t' option above).
* **-X / --xlsx:** Writes an xlsx-formatted file after user-specified individuals are removed (-r option) but before any other filtering steps are applied.
* **-z / --snppit:** (under development) Prints a file in snppit format (-Z option is also required for snppit conversion as specified above).

## Outputs
Outputs retain the input file (-x / --infile) base name, but change the output file extension depending upon format. Most file conversions result in a single file. Exceptions include Plink and Structure format. The Structure conversion creates a .distructLabels.txt file which contains a list of population numbers and their associated population names. This file can be input into [distruct](https://rosenberglab.stanford.edu/distruct.html), or used in the [CLUMPAK](http://clumpak.tau.ac.il/) pipeline for visualizing outputs of the program [Structure](https://web.stanford.edu/group/pritchardlab/structure.html). File formats are output with the file extensions in the table below. Population maps are also provided for Genepop and NewHybrids format. These provide you with the order of the samples as they appear in the converted genotype files, as well as the population for each individual (pulled from the 'Population ID' column in your input .xlsx file).

<div align="center">
  
| Format       | Extension(s)                   | Program Option |
| :----------- | :----------------------------: | :------------: |
| Binary       | .bin                           | -b             |
| Excel        | .xlsx                          | -X             |
| Genepop      | .gen; genepop.popmap.txt       | -g             |
| NewHybrids   | .newhyb; newhybrids.popmap.txt | -n             |
| Plink        | .ped and .map                  | -p             |
| SNPPIT       | .snppit                        | -z             |
| Structure    | .str; .distructLabels.txt      | -S             |
  
</div>

Loci and individuals discarded via filtering options will be written to Excel files. All outputs retain the input file (-x / --infile) base name, but change slightly according to filtering step:

<div align="center">
  
| Filtering Step                            | Name                        | Program Option |
| :---------------------------------------- | :-------------------------: | :------------: |
| Missing data proportion for individuals   | .filteredIndividuals.xlsx   | -i             |
| Missing data proportion for loci          | .filteredLoci.xlsx          | -l             |
| Monomorphic loci                          | .monomorphic.xlsx           | -m             |
| Discard unwanted populations              | .removed.pops.xlsx          | -P             |
| List of individuals for removal           | .removed.xlsx               | -r             |
| List of loci for removal                  | .removed.loci.xlsx          | -R             |
| Sex-identifying loci                      | .sexID.xlsx                 | -d             |
| Species-identifying loci                  | .speciesID.xlsx             | -s             |

</div>

A log file is also created that documents missing data proportions per individual and locus, and the number of individuals/loci removed at each step. The log file is a plain text file that retains the input file (-x / --infile) base name, but ends in .log.

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
### NewHybrids
The NewHybrids conversion allows for optional use of the 'z' option. To use this option, add an extra column to your input .xlsx file titled exactly 'ZOPT' (no quotes). The naming of the column is important so that it will be ignored in conversions for other file formats. 

Fill the column with data to designate individuals belonging to the different classes (e.g., z0 for Pure_0, z1 for Pure_1, etc). If you do not want to provide a 'z' designation for a sample then leave that cell empty and it will be ignored. Any data in the 'ZOPT' column will be transferred to your converted file exactly as it appears in your input .xlsx file, so it is important to only enter information that will be valid in a NewHybrids input file.

### SNPPIT
The SNPPIT conversion has a few special requirements that are not needed for other file formats. Firstly, a special tab-delimited snppit map file is required as supplemental input. An example of the snppit map file is included in the 'example_files' folder. Essentially, each line of this file is intended to contain all of the information of lines starting with the POP and OFFSPRING keywords, as seen on [pages 22-23 of the SNPPIT program documentation](https://github.com/eriqande/snppit/blob/master/doc/snppit_doc.pdf). However, note that the columns of the snppitmap are in a different order than they appear in the final snppit-formatted file (i.e., 'popname'\tab'POP' rather than 'POP'\tab'popname').

Secondly, the user can utilize SNPPIT's 'optional' columns as seen on [pages 24-26 of the SNPPIT program documentation](https://github.com/eriqande/snppit/blob/master/doc/snppit_doc.pdf) by including the relevant data in their input .xlsx file. To do this, add columns to your input .xlsx file with headings that exactly match the optional columns used by SNPPIT. For example, if you want to use the POPCOLUMN_SEX option in SNPPIT, then include a column named exactly POPCOLUMN_SEX in the 'Final Genotypes' worksheet of your input .xlsx file, and fill this column with the appropriate values for each individual, as necessary.

Generally, the values you input in these optional columns should exactly match the values as they would appear in the final SNPPIT file. Additional details are as follows:
* Values in the POPCOLUMN_SEX column are somewhat flexible. Case-insensitive versions of 'f' and 'female' or 'm' and 'male' will be converted to 'F' and 'M' respectively. Blank cells and any other values entered in this column will be converted to missing data ('?').
* Values in columns containing year data (POPCOLUMN_REPRO_YEARS, OFFSPRINGCOLUMN_BORN_YEAR, OFFSPRINGCOLUMN_SAMPLE_YEAR) must be valid four-digit integers.
* Currently there are no data validation measures implemented for the other two optional columns (POPCOLUMN_SPAWN_GROUP and OFFSPRINGCOLUMN_AGE_AT_SAMPLING) so please make sure anything you enter in these columns is exactly as you want it to appear in the final file.
* Unnecessary data can be left as blank cells. An example of this is that you would not need to enter sex data for OFFSPRING groups in the POPCOLUMN_SEX column.
