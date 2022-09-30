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
	convList = ['genepop','newhybrids','structure', 'snppit']
	for key, value in d.items():
		if key in convList:
			convDict[key] = value
	#print(convDict)

	gtFile = GTseq(input.args.xlsx)
	pdf = gtFile.parseFile() #returns pandas dataframe with unfiltered data
	
	# remove species-identifying SNPs (if option invoked)
	if input.args.species:
		print("Removing species-identifying SNPs")
		print("")
		speciesPdf = gtFile.removeSpecial(pdf,input.args.species) #only runs if species file is used

	# remove sex-identifying SNPs (if option invoked)
	if input.args.sexid:
		print("Removing sex-identifying SNPs")
		print("")
		speciesPdf = gtFile.removeSpecial(pdf,input.args.sexid) #only runs if sexid file is used

	pops = gtFile.getPops(pdf) #remove populations column
	pdf = gtFile.filterFile(pdf, input.args.pmissloc, input.args.pmissind) #returns pandas dataframe with filtered data

	#begin conversion process
	conversion = GTconvert(pdf, pops, input.args.twoline, input.args.snppitmap)
	conversion.convert(convDict, input.args.xlsx)

main()

raise SystemExit
