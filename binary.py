import collections
import pandas

from majmin import MajMin

class Binary():
	'Class for converting pandas dataframe to binary format'

	def __init__(self, df, popdata):
		self.pdf = df
		self.pd = popdata
		mm = MajMin(self.pdf, 0, 1, 2)
		self.recode12 = mm.getMajorMinor() #stores major/minor allele for converting to binary format. 2 = missing, 0 = major, 1 = minor

	def convert(self):
		output = list()

		output = self.makeBinary(output)
		
		return output

	def makeBinary(self, output):
		# make header and append to output
		headerList = list()
		headerList.append("Sample")
		headerList.append("Population_ID")
		columns = list(self.pdf)
		for col in columns:
			headerList.append(col)
			headerList.append("")

		headerLine = ' '.join(headerList)
		output.append(headerLine)

		for sampleName, row in self.pdf.iterrows():
			lineList = list()

			lineList.append(sampleName)
			lineList.append(self.pd[sampleName])
			
			# add population name here if desired

			for (locus, genotype) in row.items():
				alleles = self.split(str(genotype))
				
				# next line is testing for original data missing value (0) instead of binary recoded missing value (2). 
				if len(alleles) == 1 and alleles[0] == "0":
					lineList.append(self.recode12[locus][alleles[0]])
					lineList.append(self.recode12[locus][alleles[0]])
				else:
					for allele in alleles:
						lineList.append(self.recode12[locus][allele])

			lineString = ' '.join(lineList)

			output.append(lineString)

		return output
	
	def split(self, word):
		return [char for char in word]	
