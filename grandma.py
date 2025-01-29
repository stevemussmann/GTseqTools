import collections
import os
import pandas
import re

class gRandma():
	'Class for converting pandas dataframe to gRandma format'

	def __init__(self, df, log, popdata):
		self.pdf = df
		self.log = log
		self.popdata = popdata

	def convert(self):
		output = list()

		## for a biallelic marker, need to have homozygotes of each allele and 
		## heterozygotes (i.e., 3 different genotypes for a biallelic marker)
		blacklist = self.preCheck(self.pdf)
		self.writeLog(blacklist)
		if blacklist:
			self.pdf.drop(blacklist, axis=1, inplace=True)

		output = self.makeGrandma(output)
		
		return output

	def writeLog(self, blacklist):
		fh = open(self.log, 'a')
		fh.write("## gRandma conversion\n")
		fh.write("The gRandma conversion applies an additional filter.\n")
		fh.write("This verifies that each biallelic marker has:\n")
		fh.write("1. Homozygous individuals for each allele.\n")
		fh.write("2. Heterozygous individuals.\n\n")
		fh.write("If any additional loci were discarded by this filter, they are listed below:\n")
		print("The gRandma conversion applies an additional filter.")
		print("This verifies that each biallelic marker has:")
		print("1. Homozygous individuals for each allele.")
		print("2. Heterozygous individuals.")
		print("")
		print("If any additional loci were discarded by this filter, they are listed below:")
		for locus in blacklist:
			print(locus)
			fh.write(locus)
			fh.write("\n")
		print("")
		fh.write("\n")
		fh.close()
	
	def preCheck(self, df):
		alleleDict = dict()
		blacklist = list()

		for (columnName, columnData) in df.items():
			alleleDict = self.pdf[columnName].value_counts().to_dict()
			alleleDict.pop(0, None) # remove missing data values
			
			col0 = list()
			col1 = list()
			
			for genotype, count in alleleDict.items():
				col0.append(str(genotype[0]))
				col1.append(str(genotype[1]))

			set0 = set(col0)
			set1 = set(col1)

			if (len(set0) < 2) or (len(set1) < 2):
				blacklist.append(columnName)
		
		return blacklist


	def makeGrandma(self, output):

		## make header line
		headerList = list()
		headerList.append("Pop")
		headerList.append("Ind")
		
		colNames = list(self.pdf.columns) # get list of column names

		for colName in colNames:
			headerList.append(colName)
			colA2 = colName + ".A2"
			headerList.append(colA2)

		headerString = "\t".join(headerList)

		output.append(headerString)

		for sampleName, row in self.pdf.iterrows():
			lineList = list() # temporary list used to hold contents of line as it is built

			lineList.append(str(self.popdata[sampleName])) # add pop name
			lineList.append(str(sampleName)) # add sample name
			
			# deal with alleles in concatenated format of pandas dataframe
			for (locus, genotype) in row.items():
				alleles = list()
				if str(genotype) == "0":
					alleles = ["", ""]
				else:
					alleles = [genotype[0], genotype[1]]

				tempList = list()
				
				# add alleles to string
				for allele in alleles:
					lineList.append(allele)

			lineString = "\t".join(lineList)

			output.append(lineString)

		return output
