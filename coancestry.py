import pandas

class Coancestry():
	'Class for converting pandas dataframe to coancestry format'

	def __init__(self, df, popdata):
		self.pdf = df
		self.pd = popdata
		self.nucleotides = {'A': '1', 'C': '2', 'G': '3', 'T': '4', '-': '5', '0': '0'}

	def convert(self):
		lineList = list()

		# create map of population names
		# this code will break if you input > 676 populations (i.e., 26 * 26), but that number of input populations seems unlikely
		pops = list(set(self.pd.values()))
		pops.sort()
		popMap = dict()
		first=ord('A') # starting ASCII value = 65 for A
		second=ord('A')
		for pop in pops:
			codeList = list()
			codeList.append(chr(first))
			codeList.append(chr(second))
			popcode = "".join(codeList)
			if second < 90:
				second = second + 1
			else:
				first = first + 1
				second = ord('A')
			popMap[pop] = popcode

		# write list of population map codes for coancestry output file
		fh=open("coancestry.popmap.txt", 'w')
		for key, val in popMap.items():
			fh.write(key)
			fh.write("\t")
			fh.write(val)
			fh.write("\n")
		fh.close()

		# convert data for individual samples
		for sampleName, row in self.pdf.iterrows():
			sampleList = list() # list from which this row of data will be constructed
			tempName = list()
			tempName.append(popMap[self.pd[sampleName]])
			tempName.append(sampleName)
			newName = "_".join(tempName)
			sampleList.append(newName) # add sample name to list
			#sampleList.append(self.pd[sampleName]) # add population name of sample to list

			for (locus, genotype) in row.items():
				alleles = self.split(str(genotype))
				locusList = list()

				if len(alleles) == 1 and alleles[0] == '0':
					locusList.append(self.nucleotides[alleles[0]])
					locusList.append(self.nucleotides[alleles[0]])
				else:
					for allele in alleles:
						locusList.append(self.nucleotides[allele])
				locusStr = "\t".join(locusList)
				sampleList.append(locusStr)

			sampleStr = "\t".join(sampleList)
			lineList.append(sampleStr)

		return lineList

	def split(self, word):
		return [char for char in word]	
