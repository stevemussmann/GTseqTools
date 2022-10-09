#!/usr/bin/env python3

from comline import ComLine
from gtseq import GTseq
from gtconvert import GTconvert

import argparse
import pandas
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

	gtFile = GTseq(input.args.infile)
	pdf = gtFile.parseFile() #returns pandas dataframe with unfiltered data

	# remove blacklisted individuals
	if input.args.removelist:
		print("Removing individuals specified by '-r' option.")
		print("")
		removePdf = gtFile.removeInds(pdf, input.args.removelist) #only runs if '-r' option is invoked
	
	# export xlsx file after removing blacklisted individuals
	if input.args.xlsx:
		fileName = input.args.infile.replace(" ", "_") #replace spaces in original filename if they exist
		nameList = fileName.split('.')
		nameList.pop() #remove old extension
		nameList.append("prefilter")
		nameList.append("xlsx") #add new file extension
		xlsxOut = '.'.join(nameList)
		pdf.to_excel(xlsxOut, sheet_name="Final Genotypes")
	
	# remove species-identifying SNPs (if option invoked)
	if input.args.species:
		print("Removing species-identifying SNPs")
		print("")
		speciesPdf = gtFile.removeSpecial(pdf,input.args.species) #only runs if species file is used

	# remove sex-identifying SNPs (if option invoked)
	if input.args.sexid:
		print("Removing sex-identifying SNPs")
		print("")
		sexPdf = gtFile.removeSpecial(pdf,input.args.sexid) #only runs if sexid file is used

	# pull out special columns
	snppitCols = gtFile.removeSnppit(pdf) #removes optional columns for SNPPIT

	pops = gtFile.getPops(pdf) #remove populations column
	pdf = gtFile.filterFile(pdf, input.args.pmissloc, input.args.pmissind) #returns pandas dataframe with filtered data

	#begin conversion process
	conversion = GTconvert(pdf, pops, input.args.twoline, input.args.snppitmap, snppitCols, input.args.infile)
	conversion.convert(convDict)

main()

raise SystemExit
