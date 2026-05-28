import collections
import pandas

from majmin import MajMin

class Plink():
	'Class for converting pandas dataframe to Plink format'

	def __init__(self, df):
		self.pdf = df
		mm = MajMin(self.pdf, 1, 2, 0)
		self.recode12 = mm.getMajorMinor() #stores major/minor allele for converting to PLINK format. 0 = missing, 1 = major, 2 = minor

	def convert(self):
		output = list()

		output = self.makePlink(output)
		
		plinkMapOutput = self.plinkMap()
		#for line in plinkMapOutput:
		#	print(line)

		return output, plinkMapOutput

	def makePlink(self, output):
		for sampleName, row in self.pdf.iterrows():
			lineList = list()

			lineList.append(sampleName)
			lineList.append(sampleName) #adding twice - this matches behavior of PLINK output from my admixpipe pipeline

			lineList.append("0")
			lineList.append("0")
			lineList.append("0")

			lineList.append("-9")

			for (locus, genotype) in row.items():
				alleles = self.split(str(genotype))

				if len(alleles) == 1 and alleles[0] == '0':
					lineList.append(self.recode12[locus][alleles[0]])
					lineList.append(self.recode12[locus][alleles[0]])
				else:
					for allele in alleles:
						lineList.append(self.recode12[locus][allele])

			lineString = ' '.join(lineList)

			output.append(lineString)

		return output
	
	def plinkMap(self):
		output = list()

		counter=0

		for locus in self.recode12.keys():
			counter+=1
			stringList = list() #hold items to be combined into a single tab-delimited line
			#print(locus)
			stringList.append("0")

			tempList = list() #holds items for locus identifier
			tempList.append(str(counter))
			tempList.append("1")
			tempString = ':'.join(tempList)
			stringList.append(tempString)

			stringList.append("0")
			stringList.append("1")

			newstring = "\t".join(stringList)

			output.append(newstring)

		return output

	def split(self, word):
		return [char for char in word]	
