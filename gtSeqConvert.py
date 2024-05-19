#!/usr/bin/env python3

from comline import ComLine
from gtseq import GTseq
from gtconvert import GTconvert

import argparse
import collections
import os
import pandas
import re
import sys

def main():
	input = ComLine(sys.argv[1:])

	# make list of file formats; grab relevant options from argparse object
	d = vars(input.args)
	convDict = dict()
	convList = ['allelematch', 'binary', 'coancestry', 'genepop','newhybrids','plink', 'sequoia', 'structure', 'snppit']
	for key, value in d.items():
		if key in convList:
			convDict[key] = value
	#print(convDict)
	
	# modify input .xslx filename to replace space with _ and remove .xlsx extension
	fileName = input.args.infile.replace(" ", "_") #replace spaces in original filename if they exist
	fileName = re.sub('.xlsx$', '.REPLACE.xlsx', fileName)
	logfile = re.sub('.REPLACE.xlsx$', '.log', fileName)

	# make directory to hold discarded data files
	discardDir = "discardedFiles"
	if os.path.exists(discardDir) == False:
		os.mkdir(discardDir)
	
	#check if logfile exists and delete if true
	if os.path.isfile(logfile):
		os.remove(logfile)

	gtFile = GTseq(input.args.infile, logfile)
	pdf = gtFile.parseFile() #returns pandas dataframe with unfiltered data
	startPopCounts = pdf['Population ID'].value_counts() #count starting number of individuals per population

	# remove blacklisted individuals
	if input.args.removeinds:
		print("Removing individuals specified by '-r' option.")
		print("")
		removeName = re.sub('.REPLACE.xlsx$', '.removed.xlsx', fileName)
		removePdf = gtFile.removeInds(pdf, input.args.removeinds) #only runs if '-r' option is invoked
		removeName = os.path.join(discardDir, removeName)
		removePdf.to_excel(removeName, sheet_name="Final Genotypes")

	# discard individuals not found in retained populations
	if input.args.keeppops:
		print("Keeping only individuals from populations specified by '-P' option.")
		print("")
		removeName = re.sub('.REPLACE.xlsx$', '.removed.pops.xlsx', fileName)
		removePdf = gtFile.removePops(pdf, input.args.keeppops)
		removeName = os.path.join(discardDir, removeName)
		removePdf.to_excel(removeName, sheet_name="Final Genotypes")
	
	# export xlsx file after removing blacklisted individuals and populations
	if input.args.xlsx:
		prefilterName = re.sub('.REPLACE.xlsx$', '.prefilter.xlsx', fileName)
		pdf.to_excel(prefilterName, sheet_name="Final Genotypes")
	
	# remove unwanted loci (if option invoked)
	if input.args.removeloci:
		print("Removing loci specified by '-R' option.")
		print("")
		removeLociName = re.sub('.REPLACE.xlsx$', '.removed.loci.xlsx', fileName)
		removeLociPdf = gtFile.removeSpecial(pdf,input.args.removeloci) #only runs if '-R' option is used
		removeLociName = os.path.join(discardDir, removeLociName)
		removeLociPdf.to_excel(removeLociName, sheet_name="Final Genotypes")

	# remove species-identifying SNPs (if option invoked)
	if input.args.species:
		print("Removing species-identifying SNPs")
		print("")
		speciesName = re.sub('.REPLACE.xlsx$', '.speciesID.xlsx', fileName)
		speciesPdf = gtFile.removeSpecial(pdf,input.args.species) #only runs if species file is used
		speciesPdf.to_excel(speciesName, sheet_name="Final Genotypes")

	# remove sex-identifying SNPs (if option invoked)
	if input.args.sexid:
		print("Removing sex-identifying SNPs")
		print("")
		sexName = re.sub('.REPLACE.xlsx$', '.sexID.xlsx', fileName)
		sexPdf = gtFile.removeSpecial(pdf,input.args.sexid) #only runs if sexid file is used
		sexPdf['Population ID'] = pdf['Population ID']
		if 'Sex' in pdf.columns:
			sexPdf['Sex'] = pdf['Sex']
		sexPdf.to_excel(sexName, sheet_name="Final Genotypes")

	# pull out special columns
	snppitCols = gtFile.removeSnppit(pdf) #removes optional columns for SNPPIT
	newhybCols = gtFile.removeNewhyb(pdf) #removes optional columns for NewHybrids
	sexes = gtFile.removeSex(pdf) #removes optional phenotypic sex data column
	pops = gtFile.getPops(pdf) #remove populations column; variable 'pops' is a dict

	# filter based upon missing data
	pdf = gtFile.filterFile(pdf, input.args.pmissloc, input.args.pmissind, fileName, discardDir) #returns pandas dataframe with filtered data
	keep = list(pdf.index) # make list of keys remaining in pdf - used to reduce 'pops' dict to only retained individuals after missing data filtering

	# remove monomorphic loci (if option invoked)
	if input.args.monomorphic:
		print("Removing monomorphic loci")
		monoName = re.sub('.REPLACE.xlsx$', '.monomorphic.xlsx', fileName)
		monoPdf = gtFile.removeMonomorphicLoci(pdf)
		monoName = os.path.join(discardDir, monoName)
		monoPdf.to_excel(monoName, sheet_name="Final Genotypes")

	# count individuals per population after all filters have been applied
	pops = {k: pops[k] for k in keep} # reduce 'pops' dict to only individuals retained after missing data filtering
	endPopCounts = collections.Counter(pops.values()) #count ending number of individuals per population
	gtFile.printRetained(startPopCounts, endPopCounts) # print number of retained individuals to logfile
	
	#begin conversion process
	conversion = GTconvert(pdf, pops, input.args.twoline, input.args.header, input.args.snppitmap, snppitCols, newhybCols, input.args.infile)
	conversion.convert(convDict)

main()

raise SystemExit
