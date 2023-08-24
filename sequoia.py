import collections

import pandas

class Sequoia():
	'Class for converting pandas dataframe to sequoia format'

	def __init__(self, df, popdata):
		self.pdf = df
		self.pd = popdata
		self.recode12 = collections.defaultdict(dict) #stores major/minor allele for converting to binary format. 2 = missing, 0 = major, 1 = minor
		self.genotypes = {'00': '0', '11': '2', '10': '1', '01': '1', '22': '-9'} # map for converting binary format to sequoia format

	def getMajorMinor(self):
		# get counts of all genotypes at each locus and put into dictionary
		for columnName, columnData in self.pdf.items():
			self.recode12[columnName]["0"] = "2" #add missing data value to dict
			alleledict = self.pdf[columnName].value_counts().to_dict()
			allelecounts = dict() #store allele counts for this locus
			for key, value in alleledict.items():
				# ignore missing data values
				# casting as str() in next line because sometimes Excel encodes as int or string
				if str(key) != "0":
					alleles = list(key)
					for allele in alleles:
						count = allelecounts.get(allele, 0) #return 0 if key does not exist yet
						count += value
						allelecounts[allele] = count
			#determine major and minor alleles based upon counts
			major = max(allelecounts, key=allelecounts.get) #get major allele
			majCount = max(allelecounts.values())
			minor = min(allelecounts, key=allelecounts.get) #get minor allele
			minCount = min(allelecounts.values())
			
			#check number of alleles. Print warning if only 1 allele at a locus; exit program if 0 or >2 alleles at locus
			if len(allelecounts.keys()) == 1:
				print("WARNING: locus " + columnName + " is monomorphic in your dataset.")
				self.recode12[columnName][major] = "0"
			elif len(allelecounts.keys()) == 2:
				#test if equal number of alleles found
				if majCount == minCount:
					alleleNum = 0
					for key in allelecounts.keys():
						alleleNum += 1
						self.recode12[columnName][key] = str(alleleNum)
				else:
					self.recode12[columnName][major] = "0"
					self.recode12[columnName][minor] = "1"
			else:
				#unlikely to reach this code unless user turns off missing data filters or you have >2 alleles at a locus.
				num = len(allelecounts.keys())
				print("ERROR: " + str(num) + " alleles detected at " + columnName + ".")
				print("Exiting program.")
				raise SystemExit

	def convert(self, snppit):
		output = list()

		self.getMajorMinor()

		output = self.makeSequoia(output, snppit)
		
		return output

	def makeSequoia(self, output, snppit):
		print(snppit)
		# open sequoia life history file for writing
		fh=open("sequoia.LH.txt", 'w')

		for sampleName, row in self.pdf.iterrows():
			lineList = list()

			# write relevant data to life history file
			fh.write(sampleName)
			fh.write("\t")
			tempSex = str(snppit.loc[sampleName]['POPCOLUMN_SEX'])
			if tempSex.casefold() == "m" or tempSex.casefold() == "male":
				fh.write("2") # need to convert sex data to sequoia format (1 = female, 2 = male, 3 = unknown)
			elif tempSex.casefold() == "f" or tempSex.casefold() == "female":
				fh.write("1") # need to convert sex data to sequoia format (1 = female, 2 = male, 3 = unknown)
			else:
				fh.write("3") # need to convert sex data to sequoia format (1 = female, 2 = male, 3 = unknown)
			fh.write("\t")
			if snppit.isnull().loc[sampleName]["OFFSPRINGCOLUMN_BORN_YEAR"] is False:
				fh.write("-1")
			else: 
				fh.write(str(snppit.loc[sampleName]["OFFSPRINGCOLUMN_BORN_YEAR"])) # might need to pull birth year data from special column. Negative number = unknown
			fh.write("\n")

			lineList.append(sampleName)
			#lineList.append(self.pd[sampleName])
			
			# add population name here if desired

			for (locus, genotype) in row.items():
				alleles = self.split(str(genotype))
				tempList = list()
				
				# next line is testing for original data missing value (0) instead of binary recoded missing value (2). 
				if len(alleles) == 1 and alleles[0] == "0":
					tempList.append(self.recode12[locus][alleles[0]])
					tempList.append(self.recode12[locus][alleles[0]])
				else:
					for allele in alleles:
						tempList.append(self.recode12[locus][allele])
				tempString = ''.join(tempList)
				tempString = self.genotypes[tempString]
				lineList.append(tempString)

			lineString = "\t".join(lineList)

			output.append(lineString)

		# close sequoia life history file
		fh.close()

		return output
	
	def split(self, word):
		return [char for char in word]	
