from popmap import Popmap

import pandas

class Genepop():
	'Class for converting pandas dataframe to Genepop format'

	def __init__(self, df, popmap):
		self.pdf = df
		self.pops = popmap
		self.nucleotides = {'A': '01', 'C': '02', 'G': '03', 'T': '04', '-': '05', '0': '00'}
		
	def convert(self):
		pm = Popmap(self.pops)
		mapDict = pm.parseMap()

		lineList = list()

		lineList.append('Title line:""')

		for (columnName, columnData) in self.pdf.iteritems():
			lineList.append(columnName)

		for (pop, num) in mapDict.items():
			lineList.append("Pop")
			for sampleName, row in self.pdf.iterrows():
				sampleList = list()
				if self.pops[sampleName] == pop:
					sampleList.append(sampleName)
					sampleList.append(",")
					sampleList.append("")
					for (locus, genotype) in row.items():
						alleles = self.split(str(genotype))
						locusList = list()

						if len(alleles) == 1 and alleles[0] == '0':
							locusList.append(self.nucleotides[alleles[0]])
							locusList.append(self.nucleotides[alleles[0]])
						else:
							for allele in alleles:
								locusList.append(self.nucleotides[allele])
						locusStr = ''.join(locusList)
						sampleList.append(locusStr)
					sampleStr = ' '.join(sampleList)
					lineList.append(sampleStr)

		return lineList

	def split(self, word):
		return [char for char in word]
