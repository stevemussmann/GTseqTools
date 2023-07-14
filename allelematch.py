import pandas

class AlleleMatch():
	'Class for converting pandas dataframe to allelematch format'

	def __init__(self, df, popdata):
		self.pdf = df
		self.pd = popdata
		self.nucleotides = {'A': '1', 'C': '2', 'G': '3', 'T': '4', '-': '5', '0': '-99'}

	def convert(self):
		lineList = list()

		# construct header
		headList = list()

		headList.append("sampleId")
		headList.append("samplingData")

		for(columnName, columnData) in self.pdf.items():
			columnNameA = "".join([columnName, "a"])
			columnNameB = "".join([columnName, "b"])
			headList.append(columnNameA)
			headList.append(columnNameB)

		headLine = ",".join(headList)

		lineList.append(headLine)

		# convert data for individual samples
		for sampleName, row in self.pdf.iterrows():
			sampleList = list() # list from which this row of data will be constructed
			sampleList.append(sampleName) # add sample name to list
			sampleList.append(self.pd[sampleName]) # add population name of sample to list

			for (locus, genotype) in row.items():
				alleles = self.split(str(genotype))
				locusList = list()

				if len(alleles) == 1 and alleles[0] == '0':
					locusList.append(self.nucleotides[alleles[0]])
					locusList.append(self.nucleotides[alleles[0]])
				else:
					for allele in alleles:
						locusList.append(self.nucleotides[allele])
				locusStr = ','.join(locusList)
				sampleList.append(locusStr)

			sampleStr = ",".join(sampleList)
			lineList.append(sampleStr)

		return lineList

	def split(self, word):
		return [char for char in word]	
