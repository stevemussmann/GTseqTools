import pandas

class NewHybrids():
	'Class for converting GTseq genotype files'

	def __init__(self, df):
		self.pdf = df
		self.nucleotides = {'A': '01', 'C': '02', 'G': '03', 'T': '04', '-': '05', '0': '0'}
		
	def convert(self):
		output = list() #holds final file output
		# get number of individuals and loci
		nInds = len(self.pdf.axes[0])
		nLoci = len(self.pdf.axes[1])

		# construct first four lines
		first = '\t'.join(['NumIndivs', str(nInds)])
		second = '\t'.join(['NumLoci', str(nLoci)])
		third = '\t'.join(['Digits', '2'])
		fourth = '\t'.join(['Format', 'Lumped'])
		
		# develop locus header line
		headerList = ['LocusNames']
		for(columnName, columnData) in self.pdf.iteritems():
			headerList.append(columnName)

		locusHeader = '\t'.join(headerList)

		# add header lines to output
		output.append(first)
		output.append(second)
		output.append(third)
		output.append(fourth)
		output.append('') #blank line
		output.append(locusHeader)

		for sampleName, row in self.pdf.iterrows():
			lineList = [sampleName]
			lineList.append('') #blank space - can be used for 'z' option if implemented
			for (locus,genotype) in row.items():
				alleles = self.split(str(genotype))
				convertedAlleles = list()
				convertedGenotype = ''

				# check if missing data
				if len(alleles) == 1 and alleles[0] == '0':
					convertedAlleles.append('0')
				# else, split into individual alleles and convert to numbers
				else:
					for allele in alleles:
						convertedAlleles.append(self.nucleotides[allele])
				convertedGenotype = ''.join(convertedAlleles)
				lineList.append(convertedGenotype)
			indLine = '\t'.join(lineList)
			output.append(indLine) # add to output

		return output

	def split(self, word):
		return [char for char in word]
