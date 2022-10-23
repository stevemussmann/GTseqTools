from popmap import Popmap

import pandas

class Structure():
	'Class for converting pandas dataframe to Structure format'

	def __init__(self, df, popmap):
		self.pdf = df
		self.pops = popmap
		self.nucleotides = {'A': '1', 'C': '2', 'G': '3', 'T': '4', '-': '5', '0': '-9'}

	def convert(self, tBoolean, hBoolean):
		pm = Popmap(self.pops)
		mapDict = pm.parseMap()

		#get list of structure populations. number->pop
		structureMap = pm.printMap(mapDict, self.pdf)

		twoLineFormat = tBoolean
		headerFormat = hBoolean

		output = list()

		if twoLineFormat == False:
			output = self.oneLine(output, mapDict, headerFormat)
		else:
			output = self.twoLine(output, mapDict, headerFormat)
		
		return output, structureMap

	def prepareHeader(self):
		locusHeader = list()
		for locusName in self.pdf.columns:
			locusHeader.append(locusName)

		headerString = '\t'.join(locusHeader)
		return headerString

	def oneLine(self, output, mapDict, header):
		if header:
			headerString = self.prepareHeader()
			output.append(headerString)

		for sampleName, row in self.pdf.iterrows():
			lineList = list()

			lineList.append(sampleName)

			lineList.append(str(mapDict[self.pops[sampleName]]))

			for (locus, genotype) in row.items():
				alleles = self.split(str(genotype))

				if len(alleles) == 1 and alleles[0] == '0':
					lineList.append(self.nucleotides[alleles[0]])
					lineList.append(self.nucleotides[alleles[0]])
				else:
					for allele in alleles:
						lineList.append(self.nucleotides[allele])

			lineString = '\t'.join(lineList)

			output.append(lineString)

		return output

	def twoLine(self, output, mapDict, header):
		if header:
			headerString = self.prepareHeader()
			output.append(headerString)

		for sampleName, row in self.pdf.iterrows():
			lineOne = list()
			lineTwo = list()
			
			# add sample names
			lineOne.append(sampleName)
			lineTwo.append(sampleName)

			# add population numbers
			lineOne.append(str(mapDict[self.pops[sampleName]]))
			lineTwo.append(str(mapDict[self.pops[sampleName]]))

			for x in range(4):
				lineOne.append("")
				lineTwo.append("")

			for (locus, genotype) in row.items():
				alleles = self.split(str(genotype))

				if len(alleles) == 1 and alleles[0] == '0':
					lineOne.append(self.nucleotides[alleles[0]])
					lineTwo.append(self.nucleotides[alleles[0]])
				else:
					lineOne.append(self.nucleotides[alleles[0]])
					lineTwo.append(self.nucleotides[alleles[1]])

			lineOneString = '\t'.join(lineOne)
			lineTwoString = '\t'.join(lineTwo)

			output.append(lineOneString)
			output.append(lineTwoString)

		return output

	def split(self, word):
		return [char for char in word]	
