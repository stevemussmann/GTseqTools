from collections import Counter
from decimal import Decimal
from duplicates import Duplicates
from stats import GTStats

import os
import re
import sys
import numpy
import pandas
import holoviews
import matplotlib.pyplot
import scipy

holoviews.extension('bokeh')

class GTseq():
	'Class for operating on GTseq genotype files'

	def __init__(self, infile, identQuit, log):
		self.gtFile = infile
		self.logfile = log
		self.plotDir = "plots"
		self.identQuit = identQuit

		# write command used to launch program
		fh = open(self.logfile, 'a')
		fh.write("#gtSeqConvert.py was launched with command:\n#")
		comm = ' '.join(sys.argv)
		fh.write(comm)
		fh.write("\n\nAll filtering operations have been applied in the order they are presented in this log file.\n\n")
		fh.close()

		if os.path.exists(self.plotDir) == False:
			os.mkdir(self.plotDir)

		# prepare dict of lists to contain data for sankey diagrams
		sankeyKeys = ['Source', 'Filter', 'Count']
		self.sankeyIndDict = {key: [] for key in sankeyKeys}
		self.sankeyLocDict = {key: [] for key in sankeyKeys}


	# This function can only be run after the GTseq.remDupGenos() function because it will add an object of type Duplicates to this class as a member variable (self.dups)
	def plotMismatches(self):
		# mismatches is a list of numpy type np.int64
		mismatches = self.dups.returnMismatches()
		mismatchDict = dict(enumerate(mismatches)) # enumerate to add dummy key values for purpose of making dict to plot data

		# calculate stats
		mismatchStats = GTStats(mismatches)
		mismatchStats.calcStats()

		# make histogram and qq plots
		histoFN = "histogram.mismatch.png"
		qqFN = "qqplot.mismatch.png"
		mismatchHisto = os.path.join(self.plotDir, histoFN)
		mismatchQQ = os.path.join(self.plotDir, qqFN)
		self.makeMismatchHisto(mismatchDict, mismatchHisto)
		self.makeMismatchQQ(mismatchDict, mismatchQQ)

	def plotIFI(self, df, prepost):
		ifiScores = df['IFI'].tolist() # extract as list for stats calculations
		ifiScores = [Decimal(x) for x in ifiScores] # cast all list elements as Decimal
		
		ifiScoresDict = df['IFI'].to_dict() # extract as dict for plotting

		# calculate stats
		ifiStats = GTStats(ifiScores)
		ifiStats.calcStats()
		ifiStats.printStats(self.logfile, "ifi scores", prepost)
	
		# make histogram plot
		ifiFn = "histogram.ifi." + prepost + ".png"
		ifiHisto = os.path.join(self.plotDir, ifiFn)
		self.makeIFIplot(ifiScoresDict, ifiHisto)

	def makeHistos(self, df, prepost):
		deepcopy = df.copy() # make deep copy of dataframe
		print(f"\nCalculating {prepost} missing data statistics.")

		# remove metadata columns so they are not potentially counted in missing data
		metadataCols = ['Population ID', 'colony2', 'IFI', 'ZOPT', 'Sex', 'POPCOLUMN_SEX', 'POPCOLUMN_REPRO_YEARS', 'POPCOLUMN_SPAWN_GROUP', 'OFFSPRINGCOLUMN_BORN_YEAR', 'OFFSPRINGCOLUMN_SAMPLE_YEAR', 'OFFSPRINGCOLUMN_AGE_AT_SAMPLING'] # list of all possible metadata columns. All others will be treated as genotype data

		remove = list() # track list of columns to be removed
		metaCols = pandas.DataFrame() # make empty dataframe to hold removed columns

		for col in metadataCols:
			if col in deepcopy.columns:
				remove.append(col)

		if remove:
			print(f"Ignoring metadata columns for {prepost} missing data calculations and plots.\n")
			metaCols = self.removeColumns(deepcopy, remove)

		# metadata removed; can now calculate number of loci and individuals
		inds = str(len(deepcopy)) # number of individuals
		loci = str(len(deepcopy.columns)) # number of loci

		print(f"Printing {prepost} stats for {inds} individuals and {loci} loci.\n")

		# convert the '0' character from .csv files to 0 integer (as read from .xlsx files)
		deepcopy = deepcopy.replace('0', 0)
		
		# calculate pre- or post-filter proportion of missing data in loci 
		missingDictLoci = self.calcMissingLoci(deepcopy)
		lociMissVals = list(missingDictLoci.values()) # get missing data proportions as list

		# calculate pre- or post-filter missing data statistics per locus
		lociStats = GTStats(lociMissVals)
		lociStats.calcStats()
		lociStats.printStats(self.logfile, prepost, "loci")

		# plot pre- or post-filter missing loci data here
		lociFn = "histogram.loci." + prepost + ".png"
		lociHisto = os.path.join(self.plotDir, lociFn)
		self.plotMissing(missingDictLoci, lociHisto)

		# calculate pre- or post-filter missing data per individual
		missingDictInds = self.calcMissingInds(deepcopy)
		indsMissVals = list(missingDictInds.values()) # get missing data proportions as list

		# calculate pre- or post-filter missing data statistics per individual
		indsStats = GTStats(indsMissVals)
		indsStats.calcStats()
		indsStats.printStats(self.logfile, prepost, "individuals")

		# make plot of pre- or post-filter missing data per individual
		indsFn = "histogram.individuals." + prepost + ".png"
		sampPrefilterHisto = os.path.join(self.plotDir, indsFn)
		self.plotMissing(missingDictInds, sampPrefilterHisto)

		del metaCols # make sure memory used by removed columns is freed
		del deepcopy # make sure memory used by the deep copy is freed


	def printSankey(self, pdf):
		print("Writing sankey diagrams...")

		## individuals
		sankeyIndDF = pandas.DataFrame(self.sankeyIndDict) # convert sankey data to pandas dataframe
		sankeyIndDF['Count'] = pandas.to_numeric(sankeyIndDF['Count'], errors='coerce') # force count data to be numeric
		discardSum = sankeyIndDF.loc[sankeyIndDF['Source'] == 'Discarded', 'Count'].sum() # sum discarded values
		sankeyIndDF.loc[len(sankeyIndDF)] = ['All', 'Discarded', discardSum] # add discarded value sum to dataframe
		#print(sankeyIndDF, "\n")

		## loci
		self.sankeyLocDict["Source"].append("All")
		self.sankeyLocDict["Filter"].append("Retained")
		self.sankeyLocDict["Count"].append(len(pdf.columns))
		sankeyLocDF = pandas.DataFrame(self.sankeyLocDict)
		sankeyLocDF['Count'] = pandas.to_numeric(sankeyLocDF['Count'], errors='coerce') # force count data to be numeric
		discardSumLoc = sankeyLocDF.loc[sankeyLocDF['Source'] == 'Discarded', 'Count'].sum() # sum discarded values
		sankeyLocDF.loc[len(sankeyLocDF)] = ['All', 'Discarded', discardSumLoc] # add discarded value sum to dataframe
		#print(sankeyLocDF, "\n")

		sankeyInd = holoviews.Sankey(sankeyIndDF, label='Individuals') # make sankey object
		spInd = sankeyInd.opts(label_position='left', edge_color='Filter', node_color='index', cmap='tab20') # make sankey plot
		sankeyIndPath = os.path.join(self.plotDir, "sankey_plot_individuals.html") # make path for sankey output
		holoviews.save(spInd, sankeyIndPath, fmt="html") # print sankey plot - opted for html because .png and .svg options have too many dependencies
		print("Sankey diagram for individuals written to", str(sankeyIndPath))

		sankeyLoc = holoviews.Sankey(sankeyLocDF, label='Loci') # make sankey object
		spLoc = sankeyLoc.opts(label_position='left', edge_color='Filter', node_color='index', cmap='tab20') # make sankey plot
		sankeyLocPath = os.path.join(self.plotDir, "sankey_plot_loci.html") # make path for sankey output
		holoviews.save(spLoc, sankeyLocPath, fmt="html") # print sankey plot - opted for html because .png and .svg options have too many dependencies
		print("Sankey diagram for loci written to", str(sankeyLocPath), "\n")
	
	def printRetained(self, start, end, keepPops=None):
		## start is a pandas series
		## end is of type 'collections.Counter'

		fh = open(self.logfile, 'a')
		fh.write("The following table reports the number of individuals retained (Output) from each population.\n")
		fh.write("The Output(expected) value assumes missing individuals are evenly distributed among sample groups.\n")
		fh.write("Population\tInput\tOutput(observed)\tOutput(expected)\n")
		print("The following table reports the number of individuals retained (Output) from each population.")
		print("The Output(expected) value assumes missing individuals are evenly distributed among sample groups.")
		print("Population\tInput\tOutput(observed)\tOutput(expected)")

		start = start.sort_index() # sort start pandas series so table prints in consistent order

		# check if keeppops (-P) option used
		if keepPops is not None:
			discardStart = start[~start.index.isin(keepPops)]
			start = start[start.index.isin(keepPops)]
			end = Counter({k: end[k] for k in keepPops if k in end})

		#print(discardEnd)

		totalIn = start.sum() # total samples input
		totalOut = end.total() # total samples output
		pctRetained = float(totalOut / totalIn) # percentage of retained individuals

		# track retained individuals for sankey plot
		self.sankeyIndDict["Source"].append("All")
		self.sankeyIndDict["Filter"].append("Retained")
		self.sankeyIndDict["Count"].append(str(totalOut))

		obsList = list()
		expList = list()
		for k,v in start.items():
			if k in end:
				exp = self.expected(start[k], end[k], pctRetained)
				print("{}\t{}\t{}\t{}".format(k, v, end[k], "{:.2f}".format(exp)))
				fh.write(str(k) + "\t" + str(v) + "\t" + str(end[k]) + "\t" + "{:.2f}".format(exp) + "\n")
				obsList.append(float(end[k]))
				expList.append(float(exp))
			else:
				exp = self.expected(start[k], 0, pctRetained)
				print("{}\t{}\t{}\t{}".format(k, v, "0", "{:.2f}".format(exp)))
				fh.write(str(k) + "\t" + str(v) + "\t" + str("0") + "\t" + "{:.2f}".format(exp) + "\n")
				obsList.append(float(0))
				expList.append(float(exp))
		print("{}\t{}\t{}\t{}".format("Total", str(totalIn), str(totalOut), "N/A"))
		print("")
		fh.write(str("Total\t") + str(totalIn) + "\t" + str(totalOut) + "\tN/A" + "\n\n")

		# test if more than one population input and/or retained before performing chisquare test
		if len(obsList) > 1:
			try:
				# chisquare test using scipy library
				#chisq = scipy.stats.chisquare(obsList, f_exp=expList) # old code
				## folowing example from here: https://github.com/scipy/scipy/issues/12282
				expList_scaled = numpy.array(expList) * (numpy.sum(obsList) / numpy.sum(expList)) # new code
				chisq = scipy.stats.chisquare(f_obs=obsList, f_exp=expList_scaled) # new code
				df = len(obsList)-1
		
				print("Performing chi squared test to evaluate if missing individuals are evenly distributed among sample groups.")
				print("chisq\tdf\tp")
				print(str("{:.3f}".format(chisq[0])), "\t", str(df), "\t", str("{:.3f}".format(chisq[1])))
				print("")
		
				fh.write("Performing chi squared test to evaluate if missing individuals are evenly distributed among sample groups.\n")
				fh.write("chisq\tdf\tp\n")
				fh.write(str("{:.3f}".format(chisq[0])) + "\t" + str(df) + "\t" + str("{:.3f}".format(chisq[1])) + "\n\n")

			except ValueError as e:
				print("ERROR: chisquare test failed.")
				print("Error message: " + str(e))
				print("")
		else:
			print("Chi squared test not performed because only one population was analyzed.\n")
			fh.write("Chi squared test not performed because only one population was analyzed.\n\n")

		# if keeppops filter was used, print discarded populations
		if keepPops is not None:
			totalDiscardIn = discardStart.sum() # total samples input

			print("These populations were discarded by the -P / --keeppops filter:")
			print("Population\tInput\tOutput(observed)\tOutput(expected)")

			fh.write("These populations were discarded by the -P / --keeppops filter:\n")
			fh.write("Population\tInput\tOutput(observed)\tOutput(expected)\n")

			# print / write to log counts for discarded populations
			for k, v in discardStart.items():
				print("{}\t{}\t{}\t{}".format(k, v, "0", "0.0"))
				fh.write(str(k) + "\t" + str(v) + "\t" + str("0") + "\t" + "0.0\n")
			print("{}\t{}\t{}\t{}".format("Total", str(totalDiscardIn), "0", "N/A"))
			print("")
			fh.write(str("Total\t") + str(totalDiscardIn) + "\t0\tN/A\n\n")
				
		fh.close()

	def expected(self, inInds, outInds, pctRet):
		exp = inInds * pctRet

		return exp

	def parseFile(self):
		print("Reading input file.")
		print("")
		# test if .xlsx file and read it into pandas dataframe
		if self.gtFile.endswith(".xlsx"):
			with pandas.ExcelFile(self.gtFile) as xlsx:
				try:
					data = pandas.read_excel(xlsx, 'Final Genotypes', index_col=0)
				except ValueError as e:
					print("ERROR:")
					print(e)
					print("Your GTseq data must be in a worksheet named exactly \"Final Genotypes\" (no quotes).")
					print("Exiting program...")
					print("")
					raise SystemExit
		# if not .xlsx, test if .csv file and read it into pandas dataframe
		elif self.gtFile.endswith(".csv"):
			try:
				data = pandas.read_csv(self.gtFile, on_bad_lines="error", index_col=0, header=0, engine="python")
			except pandas.errors.ParserError as e:
				print(f"ERROR: Malformed CSV rows. Details: {e}")
				print("Exiting program...")
				print("")
				raise SystemExit
		# exit with error if not .xlsx or .csv
		else:
			print("Input file not .xlsx or .csv. How did you get here?\n")
			raise SystemExit

		# test for duplicate sample names
		print("Checking for duplicate sample names...")
		duplicateNames = data.index.duplicated().any()
		if duplicateNames:
			print("These sample names appeared multiple times in your input file:")
			duplicateList = data.index[data.index.duplicated()].unique().tolist()
			print(*duplicateList, sep='\n')

			if self.identQuit:
				print("ERROR: Your input .xlsx file contains duplicate sample names.")
				print("Either fix this problem in your input file or try forcing duplicated names to be unique with the -Q / --identquit option.")
				print("Exiting program...\n")
				raise SystemExit
			else:
				print("\nForcing unique names for duplicates...")
				print("The first occurrence of each name will be unmodified and subsequent occurrences will have suffixes appended (e.g., '_1', '_2', etc.)\n")
				counts = data.index.to_series().groupby(level=0).cumcount()
				data.index = data.index.where(counts == 0, data.index + '_' + counts.astype(str))

		else:
			print("None Found!\n")

		return data

	# remove duplicate individuals
	def remDupGenos(self, df, dupThresh, keepDups):
		dups = Duplicates(df, dupThresh, keepDups, self.logfile)
		dups.findDups()
		removeList = dups.removeDups() # get list of individuals to remove
		removedDups = pandas.DataFrame() # initialize empty dataframe
		if not removeList:
			print("No duplicates to be removed.")
		else:
			removedDups = self.removeRows(df, removeList)

		# track removed individuals for sankey plot
		self.sankeyIndDict["Source"].append("Discarded")
		self.sankeyIndDict["Filter"].append("keepdups")
		self.sankeyIndDict["Count"].append(str(len(removeList)))

		self.dups = dups # add Duplicates() object as member variable

		return removedDups

	def getPops(self, df):
		pops = df.pop('Population ID').to_dict()
		return pops

	def filterFile(self, df, pMissLoci, pMissInd, fileName, discardDir, order):
		# this converts the '0' character from .csv files to 0 integer (as read from .xlsx files)
		df = df.replace('0', 0)

		## REMOVE IN FUTURE REVISION - this is never being used again - why am I calculating this?
		# also calculate missing data per individual before removing loci with high missingness
		#missingDictTemp = self.calcMissingInds(df)

		# initialize empty pandas dataframes
		removedLoci = pandas.DataFrame()
		removedInds = pandas.DataFrame()

		if order == "loci":
			# start by calculating proportion of missing data in loci
			missingDictLoci = self.calcMissingLoci(df)

			# remove loci
			removedLoci = self.removeMissingLoci(missingDictLoci, df, pMissLoci)

			# calculate proportion of missing data in individuals
			missingDictInd = self.calcMissingInds(df)

			# remove individuals and print discarded data to file
			removedInds = self.removeMissingInds(missingDictInd, df, pMissInd)

		elif order == "individuals":
			# start by calculating proportion of missing data in individuals
			missingDictInd = self.calcMissingInds(df)

			# remove individuals
			removedInds = self.removeMissingInds(missingDictInd, df, pMissInd)

			# calculate proportion of missing data in loci
			missingDictLoci = self.calcMissingLoci(df)

			# remove loci and print discarded data to file
			removedLoci = self.removeMissingLoci(missingDictLoci, df, pMissLoci)

		else:
			print(f"\nERROR: requested to filter {order} first (-o / --order option).")
			print("Code should be unreachable - how did you get here?\n")
			SystemExit(1)

		# print discarded locus data to file
		lociName = re.sub('.REPLACE.xlsx$', '.filteredLoci.xlsx', fileName)
		lociName = os.path.join(discardDir, lociName)
		removedLoci.to_excel(lociName, sheet_name="Final Genotypes")

		# print discarded individual data to file
		indsName = re.sub('.REPLACE.xlsx$', '.filteredIndividuals.xlsx', fileName)
		indsName = os.path.join(discardDir, indsName)
		removedInds.to_excel(indsName, sheet_name="Final Genotypes")

		return df

	def makeMismatchHisto(self, d, histoFN):
		matplotlib.pyplot.figure().clear()
		mismatchSeries = pandas.Series(d)

		# get maximum mismatch value
		maxMismatch = mismatchSeries.max()

		# Set number of bins to number of mismatches
		binCount = maxMismatch

		# histogram plot
		mismatchSeries = pandas.to_numeric(mismatchSeries)
		histo = mismatchSeries.plot.hist(grid=False, bins=binCount, range=(0.0,maxMismatch), rwidth=0.9, color='#607c8e')
		histo.set_xlim(0.0, maxMismatch)
		fig = histo.get_figure()
		matplotlib.pyplot.title('Distribution of Genotype Mismatches')
		matplotlib.pyplot.xlabel('Mismatches')
		matplotlib.pyplot.ylabel('Counts')
		fig.savefig(histoFN, dpi=600)


	def makeMismatchQQ(self, d, qqFN):
		# qq plot
		matplotlib.pyplot.figure().clear()
		matplotlib.pyplot.figure(figsize=(6,6))
		vallist = list(d.values())
		res = scipy.stats.probplot(vallist, dist="norm", plot=matplotlib.pyplot)

		matplotlib.pyplot.title("Normal Q-Q Plot (Genotype Mismatch Counts)", fontsize=14)
		matplotlib.pyplot.xlabel("Theoretical Quantiles", fontsize=12)
		matplotlib.pyplot.ylabel("Number of Mismatching Loci", fontsize=12)
		matplotlib.pyplot.grid(True, linestyle="--", alpha=0.6)
		matplotlib.pyplot.savefig(qqFN, dpi=600, bbox_inches="tight")

	## This function is unused - leaving it here in case I want it later for any reason
	## previously called from within makeMismatchPlots() function to look for outliers in qq plot
	def calcOutliers(self, res):
		# Find the equation of the reference line (y = mx + b)
		# res[1][0] = slope (m), res[1][1] = intercept (b)
		x = res[0][0]
		y = res[0][1]
		slope = res[1][0]
		intercept = res[1][1]

		# Calculate expected y-values on the reference line and find the distance (residuals)
		expected_y = slope * x + intercept
		distances = y - expected_y

		# Set a threshold for what constitutes an "outlier"
		# Using standard deviations of the distances (4.5 standard deviations in code below)
		threshold = 4.5 * numpy.std(distances)

		# Extract the actual outlier values from your original data
		outliers = y[distances < -threshold]

		print(f"Found {len(outliers)} outlier values.")
		print("Top 10 most extreme outliers:", outliers[:10])

	def makeIFIplot(self, d, fn):
		matplotlib.pyplot.figure().clear()
		ifiSeries = pandas.Series(d)

		# get maximum IFI value
		maxIFI = ifiSeries.max()

		# give about 40 bins per 5.0 IFI score units
		binCount = int(maxIFI/0.125)

		ifiSeries = pandas.to_numeric(ifiSeries)
		histo = ifiSeries.plot.hist(grid=False, bins=binCount, range=(0.0,maxIFI), rwidth=0.9, color='#607c8e')
		histo.set_xlim(0.0, maxIFI)
		fig = histo.get_figure()
		matplotlib.pyplot.title('IFI Score Distribution')
		matplotlib.pyplot.xlabel('IFI Scores')
		matplotlib.pyplot.ylabel('Counts')
		fig.savefig(fn, dpi=600)


	def plotMissing(self, d, fn):
		matplotlib.pyplot.figure().clear()
		missSeries = pandas.Series(d)
		missSeries = pandas.to_numeric(missSeries)
		histo = missSeries.plot.hist(grid=False, bins=40, range=(0.0,1.0), rwidth=0.9, color='#607c8e')
		histo.set_xlim(0.0, 1.0)
		fig = histo.get_figure()
		matplotlib.pyplot.title('Proportion of Missing GTseq Data')
		matplotlib.pyplot.xlabel('Proportion Missing')
		matplotlib.pyplot.ylabel('Counts')
		fig.savefig(fn, dpi=600)


	def removeSpecial(self, df, snps, locfilter):
		remove = list()
		with open(snps, 'r') as fh:
			for line in fh:
				remove.append(line.strip())

		# track number of loci being removed per filter
		self.sankeyLocDict["Source"].append("Discarded")
		self.sankeyLocDict["Filter"].append(locfilter)
		self.sankeyLocDict["Count"].append(len(remove))

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
			print("IFI score column not detected in input file.\n")

		return ifiCols

	def removeColony(self, df):
		print("Checking for presence of optional Colony2 column.")
		optionalCols = ['colony2']

		remove = list()
		colonyCol = pandas.DataFrame()

		for col in optionalCols:
			if col in df.columns:
				remove.append(col)

		if remove:
			print("Colony2 column is being removed.\n")
			colonyCol = self.removeColumns(df, remove)
		else:
			print("Colony2 column not detected in input file.\n")

		return colonyCol

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
				print("ERROR at locus")
				print(columnName)
				print(e)
				print("This error occurred when calculating the proportion of missing data per locus.")
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

		self.sankeyLocDict["Source"].append("Discarded")
		self.sankeyLocDict["Filter"].append("pmissloc")
		self.sankeyLocDict["Count"].append(len(remove))

		if remove:
			junk = self.removeColumns(df, remove)

		print("")
		
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

		if remove:
			self.sankeyLocDict["Source"].append("Discarded")
			self.sankeyLocDict["Filter"].append("monomorphic")
			self.sankeyLocDict["Count"].append(len(remove))
		
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
		fh.write("Removed individuals with missing data proportion > " + str(pMissInd) + "\n")
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
			# track number of removed individuals for sankey plot
			self.sankeyIndDict["Source"].append("Discarded")
			self.sankeyIndDict["Filter"].append("pmissind")
			self.sankeyIndDict["Count"].append(str(len(removeMiss)))


		print("")

		return junk

	def	removeIFIinds(self, df, ifiCols, ifiScore):
		fh = open(self.logfile, 'a')
		fh.write("Removed individuals with IFI score > " + str(ifiScore) + "\n")
		remove = list()

		# pull out columns greater than IFI score
		toss = ifiCols[ifiCols['IFI'] > ifiScore]
	
		junk = pandas.DataFrame()

		# convert the 'toss' pandas dataframe to a list of samples to be removed
		if not toss.empty:
			# write to file
			fh.write("Individuals removed from dataset:\n")
			fh.write("Sample\tIFI\n")

			# print to terminal
			print("Individuals removed from dataset:")
			print("Sample\tIFI")

			for index, value in toss['IFI'].items():
				fh.write(str(index) + "\t" + str(value) + "\n")
				print(str(index), "\t", str(value))

			remove = toss.index.tolist()

		if remove:
			junk = self.removeRows(df, remove)
			print("\nRemoved "+ str(len(remove)) + " individuals with IFI score > " + str(ifiScore) + ".\n\n")
			fh.write("\nRemoved "+ str(len(remove)) + " individuals with IFI score > " + str(ifiScore) + ".\n\n")
		
			# track number of removed individuals for sankey plot
			self.sankeyIndDict["Source"].append("Discarded")
			self.sankeyIndDict["Filter"].append("ifi")
			self.sankeyIndDict["Count"].append(str(len(remove)))

		else:
			print("No samples had IFI scores > " + str(ifiScore) + ".\n\n")
			fh.write("\nNo samples had IFI scores > " + str(ifiScore) + ".\n\n")
		
		fh.write("\n")
		fh.close()

		return junk

	def removeInds(self, df, removeFile):
		remove = list()
		with open(removeFile, 'r') as fh:
			for line in fh:
				remove.append(line.strip())

		junk = pandas.DataFrame()

		if remove:

			# track removed individuals for sankey plot
			self.sankeyIndDict["Source"].append("Discarded")
			self.sankeyIndDict["Filter"].append("removeinds")
			self.sankeyIndDict["Count"].append(str(len(remove)))

			try:
				junk = self.removeRows(df, remove)
				print("")
			except KeyError as e:
				print("ERROR: " + removeFile + " contains individuals not found in Excel file.")
				print(e)
				print("")
				raise SystemExit
		else:
			print("WARNING: removelist option (-r) was invoked but file " + removeFile + " was empty.")
			print("")

		return junk

	# moved this to its own function so I could pass the set of kept populations to other functions
	def parseRemovePops(self, removeFile):
		popSet = set(line.strip() for line in open(removeFile))
		return popSet

	def removePops(self, df, popSet):

		junk = pandas.DataFrame()

		if popSet:
			remove = self.findInds(df, popSet)
			
			# track removed individuals for sankey plot
			self.sankeyIndDict["Source"].append("Discarded")
			self.sankeyIndDict["Filter"].append("keeppops")
			self.sankeyIndDict["Count"].append(str(len(remove)))
			
			junk = self.removeRows(df, remove)
			print("")
		else:
			print("WARNING: keeppops option (-P) was invoked but file " + removeFile + " was empty.")
			print("")

		return junk

	def findInds(self, df, popSet):
		removeSamples = list()
		
		for (sampleName, pop) in df['Population ID'].items():
			if str(pop) not in popSet:
				removeSamples.append(sampleName)

		return removeSamples

	def removeColumns(self, df, removelist):
		junk = pandas.concat([df.pop(x) for x in removelist], axis=1)
		return junk

	def removeRows(self, df, removelist):
		junk = pandas.DataFrame()
		try:
			junk = pandas.concat([self.popRow(df, x) for x in removelist], axis=0)
		except KeyError as e:
			print(f"\nWARNING while removing pandas dataframe rows: {e}")
			print("Check if this individual was in your input file. Final counts of removed individuals may be incorrect.")
		return junk
		
	def popRow(self, df, index):
		row = df.loc[[index]] #double brackets returns row as type pandas.dataframe rather than type pandas.series
		df.drop(index, inplace=True)
		return row
