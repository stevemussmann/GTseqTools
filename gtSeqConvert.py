#!/usr/bin/env python3

from comline import ComLine
from gtseq import GTseq

import pandas
import sys

def main():
	input = ComLine(sys.argv[1:])

	gtFile = GTseq(input.args.xlsx)
	pdf = gtFile.parseFile() #returns pandas dataframe with unfiltered data
	if input.args.species:
		print("Removing species-identifying SNPs")
		speciesPdf = gtFile.removeSpecial(pdf,input.args.species) #only runs if species file is used
	pops = gtFile.getPops(pdf) #remove populations column
	pdf = gtFile.filterFile(pdf, input.args.pmissloc, input.args.pmissind) #returns pandas dataframe with filtered data

	print(speciesPdf)


	
	

main()

raise SystemExit
