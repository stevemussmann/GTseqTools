import pandas

class NewHybrids():
	'Class for converting GTseq genotype files'

	def __init__(self, df, popmap):
		self.pdf = df
		self.pops = popmap
		self.nucleotides = {'A': '01', 'C': '02', 'G': '03', 'T': '04', '-': '05', '0': '0'}
		
	def convert(self, newhybCols):
		fh=open("newhybrids.popmap.txt", 'w')

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
		for(columnName, columnData) in self.pdf.items():
			headerList.append(columnName)

		locusHeader = '\t'.join(headerList)

		# add header lines to output
		output.append(first)
		output.append(second)
		output.append(third)
		output.append(fourth)
		output.append('') #blank line
		output.append(locusHeader)

		counter=0
		for sampleName, row in self.pdf.iterrows():
			counter+=1

			# write to newhybrids popmap
			fh.write(str(counter))
			fh.write("\t")
			fh.write(sampleName)
			fh.write("\t")
			fh.write(self.pops[sampleName])
			fh.write("\n")

			#lineList = [sampleName]
			lineList = [str(counter)] #newhybrids format wants consecutively numbered sample names
			if not newhybCols.empty:
				if pandas.isnull(newhybCols.loc[sampleName]['ZOPT']):
					lineList.append('')
				else:
					lineList.append(str(newhybCols.loc[sampleName]['ZOPT']))
			else:
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

		fh.close()

		return output

	def split(self, word):
		return [char for char in word]
