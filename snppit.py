from popmap import Popmap

import pandas

class Snppit():
	'Class for converting pandas dataframe to Genepop format'

	def __init__(self, df, popmap):
		self.pdf = df
		self.pops = popmap
		self.nucleotides = {'A': '101', 'C': '102', 'G': '103', 'T': '104', '-': '105', '0': '-9'}

		self.POP = list()
		self.OFFSPRING = list()
		self.offmap = dict()

	def parseSnppitMap(self, snppitmap):
		print("Parsing snppitmap")

		maplines = list()
		with open(snppitmap, 'r') as fh:
			for line in fh:
				maplines.append(line.strip())

		for line in maplines:
			splitline = line.split("\t")
			if splitline[1].casefold() == "POP".casefold():
				self.POP.append(splitline[0])
			elif splitline[1].casefold() == "OFFSPRING".casefold():
				self.OFFSPRING.append(splitline[0])
				try:
					self.offmap[splitline[0]] = splitline[2].split(",")
				except IndexError:
					print("ERROR:")
					print("Parental POP not provided for OFFSPRING " + splitline[0] + ".")
					print("Check that your snppitmap is tab delimited and the third column for OFFSPRING " + splitline[0] + " contains one or more parental POP.")
					print("")
					raise SystemExit
			else:
				print("Unrecognized value in second column of snppitmap:")
				print(splitline[1])
				print("")
				raise SystemExit

		#test if potential parental POPs for OFFSPRING are present in POP list
		for off, pops in self.offmap.items():
			for pop in pops:
				if pop not in self.POP:
					if pop != "?":
						print("ERROR:")
						print("POP " + pop + " was listed as a parental POP of OFFSPRING " + off + ", but this POP is not included in the your snppitmap.")
						print("")
						raise SystemExit
	
	def printData(self, mapDict, lineList, poplist, status):
		for (pop, num) in mapDict.items():
			if pop in poplist:
				templist = list()
				#construct population header line
				if status == "OFFSPRING":
					templist = [status, pop, ','.join(self.offmap[pop])]
				else:
					templist = [status, pop]
				popstring = ' '.join(templist)
				lineList.append(popstring)

				#print data for population
				for sampleName, row in self.pdf.iterrows():
					sampleList = list()
					if self.pops[sampleName] == pop:
						sampleList.append(sampleName)
						for (locus, genotype) in row.items():
							alleles = self.split(str(genotype))
							locusList = list()

							if len(alleles) == 1 and alleles[0] == '0':
								locusList.append(self.nucleotides[alleles[0]])
								locusList.append(self.nucleotides[alleles[0]])
							else:
								for allele in alleles:
									try:
										locusList.append(self.nucleotides[allele])
									except KeyError as e:
										print("CONVERSION NOT SUCCESSFUL")
										print("ERROR in converting alleles. The following allele was found in your input file:")
										print(str(e))
										print("Did you remember to remove sex-linked markers?")
										print("")
										raise SystemExit

							locusStr = ' '.join(locusList)
							sampleList.append(locusStr)
						sampleStr = '\t'.join(sampleList)
						lineList.append(sampleStr)
	
	def convert(self, snppitmap):
		self.parseSnppitMap(snppitmap)
		pm = Popmap(self.pops)
		mapDict = pm.parseMap()

		#make list to hold all lines that will be printed to file
		lineList = list()

		#append header lines to list
		nLoci = len(self.pdf.axes[1]) #calculate number of loci
		numlociList = ["NUMLOCI", str(nLoci)]
		numloci = ' '.join(numlociList)
		lineList.append(numloci)

		#missing data value
		lineList.append("MISSING_ALLELE -9")

		#locus genotyping error values
		for (columnName, columnData) in self.pdf.iteritems():
			templist = [columnName, "0.005"]
			locuserr = '\t'.join(templist)
			lineList.append(locuserr)

		#need to print all POP before all OFFSPRING
		self.printData(mapDict, lineList, self.POP, "POP")
		self.printData(mapDict, lineList, self.OFFSPRING, "OFFSPRING")

		return lineList

	def split(self, word):
		return [char for char in word]
