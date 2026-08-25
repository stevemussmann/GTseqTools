import os
import pandas

class Immanc():
	'Class for converting pandas dataframe to immanc format'

	def __init__(self, df, popmap):
		self.pdf = df
		self.pops = popmap
		self.nucleotides = {'A': '1', 'C': '2', 'G': '3', 'T': '4', '-': '5', '0': '-9'}
		
	def convert(self):
		lineList = list() # hold immanc formatted lines that will be printed to file

		allPops = set(self.pops.values()) # get list of populations

		for pop in sorted(allPops):
			for sampleName, row in self.pdf.iterrows():
				if self.pops[sampleName] == pop:
					for (locus, genotype) in row.items():
						sampleList = list() # make empty list to hold contents of line
						sampleList.append(sampleName) # add sample name
						sampleList.append(pop) # add population name
						sampleList.append(locus) # add locus name

						# handle alleles
						alleles = self.split(str(genotype))

						if len(alleles) == 1 and alleles[0] == '0':
							sampleList.append(self.nucleotides[alleles[0]])
							sampleList.append(self.nucleotides[alleles[0]])
						else:
							for allele in alleles:
								sampleList.append(self.nucleotides[allele])

						# add to immanc lines
						sampleStr = ' '.join(sampleList)
						lineList.append(sampleStr)

		return lineList

	def split(self, word):
		return [char for char in word]
