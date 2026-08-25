from decimal import Decimal, ROUND_HALF_EVEN

import os
import pandas
import random

class Colony():
	'Class for converting pandas dataframe to colony format'

	def __init__(self, df, cDat, droperr, genoerr, pmale, pfemale, runlen, inbreed, runname, mpoly, fpoly, colErr):
		self.df = df
		self.ldict = df.columns.tolist()

		# account for individuals removed by filters
		common_records = pandas.merge(self.df, cDat, on='Sample', how='inner')
		self.cDat = common_records.pop('colony2') # colony data (potential male parent, female parent, offspring)

		# dict to convert alleles to number-coded genotypes
		self.nucleotides = {'A': '101', 'C': '102', 'G': '103', 'T': '104', '-': '105', '0': '00'}

		self.derr = droperr # allelic dropout rate
		self.gerr = genoerr # genotyping error rate
		self.pmale = pmale # probability of father being present among candidates
		self.pfemale = pfemale # probability of mother being present among candidates
		self.runname = runname
		self.inbreed = inbreed
		self.runlen = runlen
		self.mpoly = str(mpoly) # male polygamy/monogamy
		self.fpoly = str(fpoly) # female polygamy/monogamy
		self.colErr = colErr # file of locus error rates
		self.errDict = dict() # dict of locus error rates

		# test if genotype error file used and parse if it exists
		if self.colErr != None:
			self.parseColErr()
	
	def convert(self):
		output = list()

		## check lengths of individual names; >20 characters not recognized by colony2
		# exit function early and return empty list if names are too long
		TorF = self.checkNameLengths()
		if TorF:
			print("WARNING: An empty colony2.dat file will be written. Please fix sample names and try again.")
			return output

		randseed = random.randint(1000, 9999) # 4-digit random number seed
		colonyCounts = self.cDat.str.lower().value_counts().to_dict() # counts of offspring and parents

		loci = nLoci = int(len(self.df.columns)) # number of loci in dataframe

		datasetnamelist = list()
		datasetnamelist.append("'")
		datasetnamelist.append(str(self.runname))
		datasetnamelist.append("'")
		datasetline = "".join(datasetnamelist)
		output.append(datasetline)
		output.append(datasetline)

		try:
			offspringline = str(colonyCounts["offspring"]) + "      ! Number of offspring in the sample"
		except KeyError as e:
			print("ERROR: " + str(e) + " not detected in colony2 column of your input file.")
			print("Did you specify which individuals are offspring in the colony2 column?")
			print("Exiting Program...\n\n")
			raise SystemExit

		output.append(offspringline)

		lociline = str(loci) + "       ! Number of loci"
		output.append(lociline)

		randseedline = str(randseed) + "      ! Seed for random number generator"
		output.append(randseedline)

		output.append("0         ! 0/1=Not updating/updating allele frequency")
		output.append("2         ! 2/1=Dioecious/Monoecious species")

		inbreedline = str(self.inbreed) + "         ! 0/1=Inbreeding absent/present"
		output.append(inbreedline)

		output.append("0         ! 0/1=Diploid species/HaploDiploid species")
		output.append(f"{self.mpoly}  {self.fpoly}      ! 0/1=Polygamy/Monogamy for males & females")
		output.append("0         ! 0/1 = Clone inference = No/Yes")
		output.append("1         ! 0/1=Scale full sibship=No/Yes")
		output.append("0         ! 0/1/2/3/4=No/Weak/Medium/Strong sibship prior; 4=Optimal sibship prior for Ne")
		output.append("0         ! 0/1=Unknown/Known population allele frequency")
		output.append("1         ! Number of runs")

		runlenline = str(self.runlen) + "         ! 1/2/3/4 = Short/Medium/Long/VeryLong run"
		output.append(runlenline)
		
		output.append("1         ! 0/1=Monitor method by Iterate#/Time in second")
		output.append("1         ! Monitor interval in Iterate# / in seconds")
		output.append("0         ! 0/1=DOS/Windows version")
		output.append("1         ! 0/1/2=Pair-Likelihood-Score(PLS)/Full-Likelihood(FL)/FL-PLS-combined(FPLS) method")
		output.append("2         ! 0/1/2/3=Low/Medium/High/VeryHigh precision")
		output.append("")

		# print string of locus names
		locusNames = self.getLocusNames()
		locusString = " ".join(locusNames)
		output.append(locusString)

		# print string of marker types. 0 = codominant, 1 = dominant
		mtString = self.prepValues(loci, 0)
		output.append(mtString)

		# print string of allelic dropout rates
		adrString = self.prepValues(loci, self.derr)
		output.append(adrString)

		# print string of genotyping error rates
		if not self.errDict:
			gerString = self.prepValues(loci, self.gerr)
		else:
			errList = list()
			for l in locusNames:
				val = Decimal(str(self.errDict[l])).quantize(Decimal('0.0001'), rounding=ROUND_HALF_EVEN)
				errList.append(str(val))
			gerString = " ".join(errList)
		output.append(gerString)

		
		for (sampleName, row) in self.df.iterrows():
			if self.cDat[sampleName].casefold() == "offspring".casefold():
				sampleList = list()
				locusList = list()
				sampleList.append(str(sampleName))
				for (locus, genotype) in row.items():
					if not pandas.isnull(genotype):
						if genotype == 0:
							locusList.append("0")
							locusList.append("0")
						else:
							mid = len(genotype) // 2
							a1 = genotype[:mid]
							a2 = genotype[mid:]
							a1 = self.nucleotides[a1]
							a2 = self.nucleotides[a2]
							locusList.append(str(a1))
							locusList.append(str(a2))
					else:
						locusList.append("0")
						locusList.append("0")
				locusStr = " ".join(locusList)
				sampleList.append(locusStr)
				sampleStr = " ".join(sampleList)
				output.append(sampleStr)

		output.append("")

		# set probabilities that male and/or female parent included among candidates
		if( "male" not in colonyCounts) and ("female" not in colonyCounts):
			output.append("0.0  0.0     !prob. of dad/mum included in the candidates")
		else:
			templine = list() # list to build probabilities line
			if "male" in colonyCounts:
				templine.append(str(self.pmale))
			else:
				templine.append("0.0")

			if "female" in colonyCounts:
				templine.append(str(self.pfemale))
			else:
				templine.append("0.0")

			templine.append("      !prob. of dad/mum included in the candidates")
			mfCountString = " ".join(templine)

			output.append(mfCountString)
	
		# set number of male and/or female parents
		if( "male" not in colonyCounts) and ("female" not in colonyCounts):
			output.append("0  0         !numbers of candidate males & females")
		else:
			templine = list() # list to build line from
			if "male" in colonyCounts:
				templine.append(str(colonyCounts["male"]))
			else:
				templine.append("0")

			if "female" in colonyCounts:
				templine.append(str(colonyCounts["female"]))
			else:
				templine.append("0")

			templine.append("      !numbers of candidate males & females")
			mfCountString = " ".join(templine)

			output.append(mfCountString)

		output.append("")

		# genotypes of male parent candidates go here
		if "male" in colonyCounts:
			for (sampleName, row) in self.df.iterrows():
				if self.cDat[sampleName].casefold() == "male".casefold():
					sampleList = list()
					locusList = list()
					sampleList.append(str(sampleName))
					for (locus, genotype) in row.items():
						if not pandas.isnull(genotype):
							if genotype == 0:
								locusList.append("0")
								locusList.append("0")
							else:
								mid = len(genotype) // 2
								a1 = genotype[:mid]
								a2 = genotype[mid:]
								a1 = self.nucleotides[a1]
								a2 = self.nucleotides[a2]
								locusList.append(str(a1))
								locusList.append(str(a2))
						else:
							locusList.append("0")
							locusList.append("0")
					locusStr = " ".join(locusList)
					sampleList.append(locusStr)
					sampleStr = " ".join(sampleList)
					output.append(sampleStr)

		output.append("")

		# genotypes of female parent candidates go here
		if "female" in colonyCounts:
			for (sampleName, row) in self.df.iterrows():
				if self.cDat[sampleName].casefold() == "female".casefold():
					sampleList = list()
					locusList = list()
					sampleList.append(str(sampleName))
					for (locus, genotype) in row.items():
						if not pandas.isnull(genotype):
							if genotype == 0:
								locusList.append("0")
								locusList.append("0")
							else:
								mid = len(genotype) // 2
								a1 = genotype[:mid]
								a2 = genotype[mid:]
								a1 = self.nucleotides[a1]
								a2 = self.nucleotides[a2]
								locusList.append(str(a1))
								locusList.append(str(a2))
						else:
							locusList.append("0")
							locusList.append("0")
					locusStr = " ".join(locusList)
					sampleList.append(locusStr)
					sampleStr = " ".join(sampleList)
					output.append(sampleStr)

		output.append("")
		output.append("0  0        !#known father-offspring dyads, paternity exclusion threshold")
		output.append("")
		output.append("0  0        !#known mother-offspring dyads, maternity exclusion threshold")
		output.append("")
		output.append("0           !#known paternal sibship with unknown fathers")
		output.append("")
		output.append("0           !#known maternal sibship with unknown mothers")
		output.append("")
		output.append("0           !#known paternity exclusions")
		output.append("")
		output.append("0           !#known maternity exclusions")
		output.append("")
		output.append("0           !#known paternal sibship exclusions")
		output.append("")
		output.append("0           !#known maternal sibship exclusions")
		output.append("")

		return output


	def parseColErr(self):
		print("Using user-specified error rates from", str(self.colErr))
		with open(self.colErr, 'r') as fh:
			for line in fh:
				line = line.strip() # remove endline character
				locusErr = line.split() # split line on whitespace
				if float(locusErr[1]) < self.gerr:
					self.errDict[locusErr[0]] = self.gerr # if locus error < self.gerr value, the locus will be set to self.gerr. This is because it is unlikely any locus actually has 0 genotyping error. 
				else:
					self.errDict[locusErr[0]] = locusErr[1]


	def checkNameLengths(self):
		for (sampleName, row) in self.df.iterrows():
			nameLen = len(sampleName)
			if nameLen > 20:
				nameLenStr = str(nameLen)
				print("WARNING: Colony2 file cannot be written because at least one sample name is >20 characters long.")
				print(f"For example: {sampleName} is {nameLenStr} characters long.")
				return True # return true if names too long
		return False # return false if no names exceed threshold


	def getLocusNames(self):
		colNames = list(self.df.columns) #get column names from pandas dataframe
		return colNames


	def prepValues(self, nloci, val):
		valList = [str(val)] * nloci
		valString = " ".join(valList)
		return valString
		
