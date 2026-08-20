import os
import pandas

class Rubias():
	'Class for converting pandas dataframe to rubias format'

	def __init__(self, df, popmap, convDir):
		self.pdf = df
		self.pops = popmap
		self.convertedDir = convDir
		
	def convert(self):
		lineList = list() # hold lines to be printed in .csv format

		# make header line
		headerList = list() # list that holds contents of header line while it is built
		headerList.append("sample_type")
		headerList.append("repunit")
		headerList.append("collection")
		headerList.append("indiv")
		for (columnName, columnData) in self.pdf.items():
			allele1 = f"{columnName}_1" 
			allele2 = f"{columnName}_2"
			headerList.append(allele1)
			headerList.append(allele2)

		# make header and append to lineList
		header = ",".join(headerList)
		lineList.append(header)

		# make individual lines
		for sampleName, row in self.pdf.iterrows():
			sampleList = list() # holds line contents for each sample while line is built.

			sampleList.append("mixture") # sample_type
			sampleList.append("NA") # repunit
			sampleList.append(str(self.pops[sampleName])) # collection
			sampleList.append(sampleName) # indiv

			for (locus, genotype) in row.items():
				alleles = self.split(str(genotype))

				if len(alleles) == 1 and alleles[0] == '0':
					sampleList.append("NA")
					sampleList.append("NA")
				else:
					for allele in alleles:
						sampleList.append(allele)

			sampleString = ','.join(sampleList)

			lineList.append(sampleString)


		return lineList

	def split(self, word):
		return [char for char in word]
