#!/usr/bin/env python3

from comline import ComLine
from gtseq import GTseq
from gtconvert import GTconvert

import argparse
import os
import pandas
import re
import sys

def main():
	input = ComLine(sys.argv[1:])

	# make list of file formats; grab relevant options from argparse object
	d = vars(input.args)
	convDict = dict()
	convList = ['genepop','newhybrids','plink', 'structure', 'snppit']
	for key, value in d.items():
		if key in convList:
			convDict[key] = value
	#print(convDict)
	
	# modify input .xslx filename to replace space with _ and remove .xlsx extension
	fileName = input.args.infile.replace(" ", "_") #replace spaces in original filename if they exist
	fileName = re.sub('.xlsx$', '.REPLACE.xlsx', fileName)
	logfile = re.sub('.REPLACE.xlsx$', '.log', fileName)
	
	#check if logfile exists and delete if true
	if os.path.isfile(logfile):
		os.remove(logfile)

	gtFile = GTseq(input.args.infile, logfile)
	pdf = gtFile.parseFile() #returns pandas dataframe with unfiltered data

	# remove blacklisted individuals
	if input.args.removelist:
		print("Removing individuals specified by '-r' option.")
		print("")
		removeName = re.sub('.REPLACE.xlsx$', '.removed.xlsx', fileName)
		removePdf = gtFile.removeInds(pdf, input.args.removelist) #only runs if '-r' option is invoked
		removePdf.to_excel(removeName, sheet_name="Final Genotypes")
	
	# export xlsx file after removing blacklisted individuals
	if input.args.xlsx:
		prefilterName = re.sub('.REPLACE.xlsx$', '.prefilter.xlsx', fileName)
		pdf.to_excel(prefilterName, sheet_name="Final Genotypes")
	
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
		sexPdf.to_excel(sexName, sheet_name="Final Genotypes")

	# pull out special columns
	snppitCols = gtFile.removeSnppit(pdf) #removes optional columns for SNPPIT

	pops = gtFile.getPops(pdf) #remove populations column
	pdf = gtFile.filterFile(pdf, input.args.pmissloc, input.args.pmissind, fileName) #returns pandas dataframe with filtered data

	#begin conversion process
	conversion = GTconvert(pdf, pops, input.args.twoline, input.args.header, input.args.snppitmap, snppitCols, input.args.infile)
	conversion.convert(convDict)

main()

raise SystemExit
