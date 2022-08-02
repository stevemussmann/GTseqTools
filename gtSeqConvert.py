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
	convList = ['genepop','newhybrids','structure']
	for key, value in d.items():
		if key in convList:
			convDict[key] = value
	print(convDict)

	gtFile = GTseq(input.args.xlsx)
	pdf = gtFile.parseFile() #returns pandas dataframe with unfiltered data
	if input.args.species:
		print("Removing species-identifying SNPs")
		speciesPdf = gtFile.removeSpecial(pdf,input.args.species) #only runs if species file is used
	pops = gtFile.getPops(pdf) #remove populations column
	pdf = gtFile.filterFile(pdf, input.args.pmissloc, input.args.pmissind) #returns pandas dataframe with filtered data

	print(speciesPdf)

	#begin conversion process
	conversion = GTconvert(pdf, pops, input.args.twoline)
	conversion.convert(convDict)

#	for line in output:
#		print(line)


	
	

main()

raise SystemExit
