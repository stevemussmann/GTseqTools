import collections
import pandas

class MajMin():
	'Class for identifying major and minor alleles'

	def __init__(self, df, mj, mn, ms):
		self.mj = mj # major allele value
		self.mn = mn # minor allele value
		self.ms = ms # missing allele value
		self.pdf = df
		self.recode12 = collections.defaultdict(dict) #stores major/minor allele for converting to binary format. 2 = missing, 0 = major, 1 = minor

	def getMajorMinor(self):
		# get counts of all genotypes at each locus and put into dictionary
		for columnName, columnData in self.pdf.items():
			self.recode12[columnName]["0"] = str(self.ms) #add missing data value to dict
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
				self.recode12[columnName][major] = str(self.mj)
			elif len(allelecounts.keys()) == 2:
				#test if equal number of alleles found
				if majCount == minCount:
					alleleNum = self.mj # not a string here because using math
					for key in allelecounts.keys():
						self.recode12[columnName][key] = str(alleleNum)
						alleleNum += 1
				else:
					self.recode12[columnName][major] = str(self.mj)
					self.recode12[columnName][minor] = str(self.mn)
			else:
				#unlikely to reach this code unless user turns off missing data filters or you have >2 alleles at a locus.
				num = len(allelecounts.keys())
				print("ERROR: " + str(num) + " alleles detected at " + columnName + ".")
				print("Exiting program.")
				raise SystemExit

		return self.recode12
