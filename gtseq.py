from decimal import Decimal
from stats import GTStats

import os
import re
import sys
import pandas
import matplotlib.pyplot

class GTseq():
	'Class for operating on GTseq genotype files'

	def __init__(self, infile, log):
		self.gtFile = infile
		self.logfile = log
		self.plotDir = "plots"

		# write command used to launch program
		fh = open(self.logfile, 'a')
		fh.write("#gtSeqConvert.py was launched with command:\n#")
		comm = ' '.join(sys.argv)
		fh.write(comm)
		fh.write("\n\n")
		fh.close()

		if os.path.exists(self.plotDir) == False:
			os.mkdir(self.plotDir)
	
	def printRetained(self, start, end):
		fh = open(self.logfile, 'a')
		fh.write("The following table reports the number of individuals retained (Output) from each population:\n")
		fh.write("Population\tInput\tOutput\n")
		print("The following table reports the number of individuals retained (Output) from each population:")
		print("Population\tInput\tOutput")
		totalIn = 0
		totalOut = 0
		for k,v in start.items():
			totalIn = totalIn + int(v)
			if k in end:
				print("{}\t{}\t{}".format(k, v, end[k]))
				fh.write(str(k))
				fh.write("\t")
				fh.write(str(v))
				fh.write("\t")
				fh.write(str(end[k]))
				fh.write("\n")
				totalOut = totalOut + int(end[k])
			else:
				print("{}\t{}\t{}".format(k, v, "0"))
				fh.write(str(k))
				fh.write("\t")
				fh.write(str(v))
				fh.write("\t")
				fh.write(str("0"))
				fh.write("\n")
		print("{}\t{}\t{}".format("Total", str(totalIn), str(totalOut)))
		print("")
		fh.write(str("Total\t"))
		fh.write(str(totalIn))
		fh.write(str("\t"))
		fh.write(str(totalOut))
		fh.write(str("\n\n"))
		fh.close()

	def parseFile(self):
		print("Reading input xlsx file.")
		print("")
		with pandas.ExcelFile(self.gtFile) as xlsx:
			data = pandas.read_excel(xlsx, 'Final Genotypes', index_col=0)

		return data

	def getPops(self, df):
		pops = df.pop('Population ID').to_dict()
		return pops

	def filterFile(self, df, pMissLoci, pMissInd, fileName, discardDir):
		# start by calculating proportion of missing data in loci
		missingDictLoci = self.calcMissingLoci(df)
		# plot missing loci data here
		lociPrefilterHisto = os.path.join(self.plotDir, "histogram.loci.prefilter.png")
		self.plotMissing(missingDictLoci, lociPrefilterHisto)

		# also calculate missing data per individual before removing loci with high missingness
		missingDictTemp = self.calcMissingInds(df)
		# make plot of pre-filter missing data per individual
		sampPrefilterHisto = os.path.join(self.plotDir, "histogram.samples.prefilter.png")
		self.plotMissing(missingDictTemp, sampPrefilterHisto)

		removedLoci = self.removeMissingLoci(missingDictLoci, df, pMissLoci)
		lociName = re.sub('.REPLACE.xlsx$', '.filteredLoci.xlsx', fileName)
		lociName = os.path.join(discardDir, lociName)
		removedLoci.to_excel(lociName, sheet_name="Final Genotypes")

		missingDictInd = self.calcMissingInds(df)

		# put plotting of missingDict here - do I need this?
		#self.plotMissing(missingDictInd, "histogram.samples.prefilter.png")

		removedInds = self.removeMissingInds(missingDictInd, df, pMissInd)
		indsName = re.sub('.REPLACE.xlsx$', '.filteredIndividuals.xlsx', fileName)
		indsName = os.path.join(discardDir, indsName)
		removedInds.to_excel(indsName, sheet_name="Final Genotypes")

		return df

	def plotMissing(self, d, fn):
		matplotlib.pyplot.figure().clear()
		missSeries = pandas.Series(d)
		missSeries = pandas.to_numeric(missSeries)
		#print(missSeries)
		histo = missSeries.plot.hist(grid=False, bins=40, range=(0.0,1.0), rwidth=0.9, color='#607c8e')
		histo.set_xlim(0.0, 1.0)
		fig = histo.get_figure()
		matplotlib.pyplot.title('Proportion of Missing GTseq Data')
		matplotlib.pyplot.xlabel('Proportion Missing')
		matplotlib.pyplot.ylabel('Counts')
		#matplotlib.pyplot.grid(axis='y', alpha=0.75)
		fig.savefig(fn, dpi=300)


	def removeSpecial(self, df, snps):
		remove = list()
		with open(snps, 'r') as fh:
			for line in fh:
				remove.append(line.strip())

		junk = self.removeColumns(df, remove)
		return junk

	def removeIFI(self, df):
		print("Checking for presence of IFI score column.")
		optionalCols = ['IFI']

		remove = list()
		ifiCols = pandas.DataFrame()

		for col in optionalCols:
			if col in df.columns:
				remove.append(col)

		if remove:
			print("IFI score column is being removed.")
			ifiCols = self.removeColumns(df, remove)
		else:
			print("IFI score column not detected in input file.")
			print("")

		return ifiCols
	
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

	def removeSex(self, df):
		print("Checking for presence of optional column containing phenotypic sex data.")
		optionalCols = ['Sex']

		remove = list()
		sexCols = pandas.DataFrame()

		for col in optionalCols:
			if col in df.columns:
				remove.append(col)

		if remove:
			print("The phenotypic sex data column is being removed.")
			for col in remove:
				print(col)
			print("")
			sexCols = self.removeColumns(df, remove)
		else:
			print("Phenotypic sex column not detected in input file.")
			print("")

		return sexCols
	
	def removeNewhyb(self, df):
		print("Checking for presence of optional Newhybrids columns.")
		optionalCols = ['ZOPT']

		remove = list() #will hold list of snppit columns that appear in pandas df
		newhybCols = pandas.DataFrame() #declare empty dataframe to be returned even if no optional columns were used. 

		for col in optionalCols:
			if col in df.columns:
				remove.append(col) #add existing cols to remove list

		if remove:
			print("The following optional NewHybrids columns were detected in the input file:")
			for col in remove:
				print(col)
			print("")
			newhybCols = self.removeColumns(df, remove)
		else:
			print("No optional NewHybrids columns detected in input file.")
			print("")

		return newhybCols

	def calcMissingLoci(self, df):
		print("Calculating missing data per locus.")
		missingDict = dict()
		numInds = len(df)
		for (columnName, columnData) in df.items():
			alleledict = df[columnName].value_counts().to_dict() #convert type pandas.Series to dict
			
			# add a 0 key to the dict if there is no 0 key
			if 0 not in alleledict.keys():
				alleledict[0] = 0

			try:
				missing=Decimal(alleledict[0]/numInds)
			except ZeroDivisionError as e:
				print("ERROR:")
				print(e)
				print("This error occurred when calculating the proportion of mising data per locus.")
				print("Exiting program...")
				print("")
				raise SystemExit

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
		# plot missing data from removeMiss Dict
		lociPostfilterRemovedHisto = os.path.join(self.plotDir, "histogram.loci.removed.postfilter.png")
		self.plotMissing(removeMiss, lociPostfilterRemovedHisto)
		removeStats = GTStats(removeMiss)
		removeStats.calcStats()
		removeStats.printStats(self.logfile, "removed", "loci")
	
		# plot missing data from removeMiss Dict
		lociPostfilterRetainedHisto = os.path.join(self.plotDir, "histogram.loci.retained.postfilter.png")
		self.plotMissing(keepMiss, lociPostfilterRetainedHisto)
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
			try:
				missing = Decimal(numMissing/numLoci)
			except ZeroDivisionError as e:
				print("ERROR:")
				print(e)
				print("This error occurred when calculating the proportion of mising data per individual.")
				print("This could result if all loci were discarded by missing data filter (option -l).")
				print("Exiting program...")
				print("")
				raise SystemExit

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

		## calculate statistics
		# plot missing data from removeMiss Dict
		sampPostfilterRemovedHisto = os.path.join(self.plotDir, "histogram.samples.removed.postfilter.png")
		self.plotMissing(removeMiss, sampPostfilterRemovedHisto)
		removeStats = GTStats(removeMiss)
		removeStats.calcStats()
		removeStats.printStats(self.logfile, "removed", "individuals")
	
		# plot missing data from removeMiss Dict
		sampPostfilterRetainedHisto = os.path.join(self.plotDir, "histogram.samples.retained.postfilter.png")
		self.plotMissing(keepMiss, sampPostfilterRetainedHisto)
		keepStats = GTStats(keepMiss)
		keepStats.calcStats()
		keepStats.printStats(self.logfile, "retained", "individuals")

		return junk

	def	removeIFIinds(self, df, ifiCols, ifiScore):
		remove = list()

		# pull out columns greater than IFI score
		toss = ifiCols[ifiCols['IFI'] > ifiScore]
	
		junk = pandas.DataFrame()

		# convert the 'toss' pandas dataframe to a list of samples to be removed
		if not toss.empty:
			remove = toss.index.tolist()

		if remove:
			junk = self.removeRows(df, remove)
			print("")
		else:
			print("No samples had IFI scores > " + str(ifiScore) + ".")
			print("")

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

	def removePops(self, df, removeFile):
		popSet = set(line.strip() for line in open(removeFile))

		junk = pandas.DataFrame()

		if popSet:
			remove = self.findInds(df, popSet)
			junk = self.removeRows(df, remove)
			print("")
		else:
			print("WARNING: keeppops option (-P) was invoked but file " + removeFile + " was empty.")
			print("")

		return junk

	def findInds(self, df, popSet):
		removeSamples = list()
		
		for (sampleName, pop) in df['Population ID'].items():
			if pop not in popSet:
				removeSamples.append(sampleName)

		return removeSamples

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
