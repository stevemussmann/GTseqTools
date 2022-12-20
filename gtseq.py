from decimal import Decimal
from stats import GTStats

import os.path
import re
import sys
import pandas

class GTseq():
	'Class for operating on GTseq genotype files'

	def __init__(self, infile, log):
		self.gtFile = infile
		self.logfile = log

	def parseFile(self):
		print("Reading input xlsx file.")
		print("")
		with pandas.ExcelFile(self.gtFile) as xlsx:
			data = pandas.read_excel(xlsx, 'Final Genotypes', index_col=0)

		return data

	def getPops(self, df):
		pops = df.pop('Population ID').to_dict()
		return pops

	def filterFile(self, df, pMissLoci, pMissInd, fileName):
		missingDictLoci = self.calcMissingLoci(df)
		removedLoci = self.removeMissingLoci(missingDictLoci, df, pMissLoci)
		lociName = re.sub('.REPLACE.xlsx$', '.filteredLoci.xlsx', fileName)
		removedLoci.to_excel(lociName, sheet_name="Final Genotypes")

		missingDictInd = self.calcMissingInds(df)
		removedInds = self.removeMissingInds(missingDictInd, df, pMissInd)
		indsName = re.sub('.REPLACE.xlsx$', '.filteredIndividuals.xlsx', fileName)
		removedInds.to_excel(indsName, sheet_name="Final Genotypes")

		return df

	def removeSpecial(self, df, snps):
		remove = list()
		with open(snps, 'r') as fh:
			for line in fh:
				remove.append(line.strip())

		junk = self.removeColumns(df, remove)
		return junk
	
	def removeSnppit(self, df):
		print("Checking for presence of optional SNPPIT columns.")
		#list of all possible optional snppit columns
		optionalCols = ['POPCOLUMN_SEX', 'POPCOLUMN_REPRO_YEARS', 'POPCOLUMN_SPAWN_GROUP', 'OFFSPRINGCOLUMN_BORN_YEAR', 'OFFSPRINGCOLUMN_SAMPLE_YEAR', 'OFFSPRINGCOLUMN_AGE_AT_SAMPLING']

		remove = list() #will hold list of snppit columns that appear in pandas df
		snppitCols = pandas.DataFrame() #declare empty dataframe to be returned even if no optional columns were used. 

		for col in optionalCols:
			if col in df.columns:
				remove.append(col) #add existing cols to remove list

		if remove:
			print("The following optional SNPPIT columns were detected in the input file:")
			for col in remove:
				print(col)
			print("")
			snppitCols = self.removeColumns(df, remove)
		else:
			print("No optional SNPPIT columns detected in input file.")
			print("")

		return snppitCols

	def calcMissingLoci(self, df):
		print("Calculating missing data per locus.")
		missingDict = dict()
		numInds = len(df)
		for (columnName, columnData) in df.items():
			alleledict = df[columnName].value_counts().to_dict() #convert type pandas.Series to dict
			
			# add a 0 key to the dict if there is no 0 key
			if 0 not in alleledict.keys():
				alleledict[0] = 0

			missing=Decimal(alleledict[0]/numInds)
			
			missingDict[columnName] = missing

		return missingDict

	def removeMissingLoci(self, missingDict, df, pMissLoci):
		fh = open(self.logfile, 'a')
		print("Removing loci with missing data proportion >", pMissLoci)
		fh.write("Removed loci with missing data proportion > ")
		fh.write(str(pMissLoci))
		fh.write("\n")

		remove = list()
		removeMiss = list()
		keepMiss = list()

		print("Loci removed from dataset:")
		print("Locus\tMissing")
		
		fh.write("Loci removed from dataset:\n")
		fh.write("Locus\tMissing\n")

		for (key, value) in missingDict.items():
			if value > Decimal(pMissLoci):
				print(key, "\t", format(value, ".3f"))
				fh.write(key)
				fh.write("\t")
				fh.write(format(value, ".3f"))
				fh.write("\n")
				remove.append(key)
				removeMiss.append(value)
			else:
				keepMiss.append(value)

		fh.write("\n")
		fh.close()

		junk = pandas.DataFrame()

		if remove:
			junk = self.removeColumns(df, remove)

		print("")
		
		# calculate statistics
		removeStats = GTStats(removeMiss)
		removeStats.calcStats()
		removeStats.printStats(self.logfile, "removed", "loci")
	
		keepStats = GTStats(keepMiss)
		keepStats.calcStats()
		keepStats.printStats(self.logfile, "retained", "loci")

		return junk

	def removeMonomorphicLoci(self, df):
		fh = open(self.logfile, 'a')

		remove = list()

		for columnName, columnData in df.items():
			alleledict = df[columnName].value_counts().to_dict()
			counter = 0
			for key, value in alleledict.items():
				if str(key) != "0":
					counter+=1
			if counter == 1:
				remove.append(columnName)

		junk = pandas.DataFrame()

		if remove:
			print(str(len(remove)) + " loci were removed because they were monomorphic:")
			fh.write(str(len(remove)))
			fh.write(" loci were removed because they were monomorphic:\n")
			for loc in remove:
				print(loc)
				fh.write(loc)
				fh.write("\n")

			print("")
			fh.write("\n")

			junk = self.removeColumns(df, remove)
		else:
			print("No monomorphic loci detected.")
			print("")
			fh.write("No monomorphic loci detected.\n\n")

		fh.close()

		return junk

	def calcMissingInds(self, df):
		print("Calculating missing data per individual.")
		missingInd = dict()
		numLoci = len(df.columns)

		for (rowName, rowData) in df.iterrows():
			numMissing = 0
			for (locus, genotype) in rowData.items():
				if genotype == 0:
					numMissing = numMissing+1
			missing = Decimal(numMissing/numLoci)
			missingInd[rowName] = missing

		return missingInd
	
	def removeMissingInds(self, missingDict, df, pMissInd):
		fh = open(self.logfile, 'a')
		fh.write("Removed individuals with missing data proportion > ")
		fh.write(str(pMissInd))
		fh.write("\n")
		print("Removing individuals with missing data proportion >", pMissInd)

		remove = list()
		removeMiss = list() # list to hold missing data proportion of each removed individual
		keepMiss = list() # list to hold missing data proportion of each kept individual

		print("Individuals removed from dataset:")
		print("Sample\tMissing")
		
		fh.write("Individuals removed from dataset:\n")
		fh.write("Sample\tMissing\n")

		for (key, value) in missingDict.items():
			if value > Decimal(pMissInd):
				print(key, "\t", format(value, ".3f"))
				fh.write(key)
				fh.write("\t")
				fh.write(format(value, ".3f"))
				fh.write("\n")
				remove.append(key)
				removeMiss.append(value)
			else:
				keepMiss.append(value)

		fh.write("\n")
		fh.close()
		
		junk = pandas.DataFrame()

		if remove:
			junk = self.removeRows(df, remove)

		print("")

		# calculate statistics
		removeStats = GTStats(removeMiss)
		removeStats.calcStats()
		removeStats.printStats(self.logfile, "removed", "individuals")
	
		keepStats = GTStats(keepMiss)
		keepStats.calcStats()
		keepStats.printStats(self.logfile, "retained", "individuals")

		return junk

	def removeInds(self, df, removeFile):
		remove = list()
		with open(removeFile, 'r') as fh:
			for line in fh:
				remove.append(line.strip())

		junk = pandas.DataFrame()

		if remove:
			junk = self.removeRows(df, remove)
			print("")
		else:
			print("WARNING: removelist option (-r) was invoked but file " + removeFile + " was empty.")
			print("")

		return junk
	
	def removeColumns(self, df, removelist):
		junk = pandas.concat([df.pop(x) for x in removelist], axis=1)
		return junk

	def removeRows(self, df, removelist):
		junk = pandas.concat([self.popRow(df, x) for x in removelist], axis=0)
		return junk
		
	def popRow(self, df, index):
		row = df.loc[[index]] #double brackets returns row as type pandas.dataframe rather than type pandas.series
		df.drop(index, inplace=True)
		return row
