#from popmap import Popmap
import collections

import pandas

class Plink():
	'Class for converting pandas dataframe to Plink format'

	def __init__(self, df):
		self.pdf = df
		self.recode12 = collections.defaultdict(dict) #stores major/minor allele for converting to PLINK format. 0 = missing, 1 = major, 2 = minor

	def getMajorMinor(self):
		# get counts of all genotypes at each locus and put into dictionary
		for columnName, columnData in self.pdf.iteritems():
			self.recode12[columnName]["0"] = "0" #add missing data value to dict
			alleledict = self.pdf[columnName].value_counts().to_dict()
			allelecounts = dict() #store allele counts for this locus
			for key, value in alleledict.items():
				# ignore missing data values
				if key != 0:
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
				self.recode12[columnName][major] = "1"
			elif len(allelecounts.keys()) == 2:
				#test if equal number of alleles found
				if majCount == minCount:
					alleleNum = 0
					for key in allelecounts.keys():
						alleleNum += 1
						self.recode12[columnName][key] = str(alleleNum)
				else:
					self.recode12[columnName][major] = "1"
					self.recode12[columnName][minor] = "2"
			else:
				#unlikely to reach this code unless user turns off missing data filters or you have >2 alleles at a locus.
				num = len(allelecounts.keys())
				print("ERROR: " + str(num) + " alleles detected at " + columnName + ".")
				print("Exiting program.")
				raise SystemExit

	def convert(self):
		output = list()

		self.getMajorMinor()

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
