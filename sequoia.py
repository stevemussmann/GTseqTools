import collections
import os
import pandas

from majmin import MajMin

class Sequoia():
	'Class for converting pandas dataframe to sequoia format'

	def __init__(self, df, popdata, convDir):
		self.pdf = df
		self.pd = popdata
		mm = MajMin(self.pdf, 0, 1, 2)
		self.recode12 = mm.getMajorMinor() #stores major/minor allele for converting to binary format. 2 = missing, 0 = major, 1 = minor
		self.genotypes = {'00': '0', '11': '2', '10': '1', '01': '1', '22': '-9'} # map for converting binary format to sequoia format
		self.convertedDir = convDir

	def convert(self, snppit):
		output = list()

		output = self.makeSequoia(output, snppit)
		
		return output

	def makeSequoia(self, output, snppit):
		print(snppit)
		# open sequoia life history file for writing
		popmapOut = os.path.join(self.convertedDir, "sequoia.LH.txt")
		fh=open(popmapOut, 'w')

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
				try:
					tempString = self.genotypes[tempString]
				except KeyError as e:
					print("Problem converting locus" + locus + "for individual" + sampleName + "to create Sequoia output.")
					print("Problem key when accessing recoded allele hash:" + e)
					print("Exiting program...")
					print("")
					print("")
					raise SystemExit
				lineList.append(tempString)

			lineString = "\t".join(lineList)

			output.append(lineString)

		# close sequoia life history file
		fh.close()

		return output
	
	def split(self, word):
		return [char for char in word]	
