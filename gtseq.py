from decimal import Decimal

import os.path
import sys
import pandas

class GTseq():
	'Class for operating on GTseq genotype files'

	def __init__(self, infile):
		self.gtFile = infile

	def parseFile(self):
		with pandas.ExcelFile(self.gtFile) as xlsx:
			data = pandas.read_excel(xlsx, 'Final Genotypes', index_col=0)

		return data

	def getPops(self, df):
		pops = df.pop('Population ID').to_dict()
		return pops

	def filterFile(self, df, pMissLoci, pMissInd):
		missingDictLoci = self.calcMissingLoci(df)
		removedLoci = self.removeMissingLoci(missingDictLoci, df, pMissLoci)

		missingDictInd = self.calcMissingInds(df)
		removedInds = self.removeMissingInds(missingDictInd, df, pMissInd)

		return df

	def removeSpecial(self, df, snps):
		remove = list()
		with open(snps, 'r') as fh:
			for line in fh:
				remove.append(line.strip())

		junk = self.removeColumns(df, remove)
		return junk

	def calcMissingLoci(self, df):
		missingDict = dict()
		numInds = len(df)
		for (columnName, columnData) in df.iteritems():
			alleledict = df[columnName].value_counts().to_dict() #convert type pandas.Series to dict
			
			# add a 0 key to the dict if there is no 0 key
			if 0 not in alleledict.keys():
				alleledict[0] = 0

			missing=Decimal(alleledict[0]/numInds)
			
			missingDict[columnName] = missing

		return missingDict

	def removeMissingLoci(self, missingDict, df, pMissLoci):
		remove = list()

		for (key, value) in missingDict.items():
			if value > Decimal(pMissLoci):
				remove.append(key)

		junk = self.removeColumns(df, remove)

		return junk

	def calcMissingInds(self, df):
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
		remove = list()

		for (key, value) in missingDict.items():
			if value > Decimal(pMissInd):
				remove.append(key)

		junk = self.removeRows(df, remove)
		
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
