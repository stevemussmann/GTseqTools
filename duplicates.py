import numpy
import pandas

from itertools import combinations

class Duplicates():
	'Class for finding duplicates in pandas dataframe'

	def __init__(self, df, t, k, l):
		self.npArr = df.to_numpy() # convert pandas df to numpy array
		self.origIndex = df.index.to_numpy() # retain original indexes to lookup matching samples
		self.thresh = t # threshold for mismatches
		self.keep = k # method for keeping duplicates
		self.log = l # log file

		# lists of duplicates
		self.first = list()
		self.second = list()

	def findDups(self):
		print(f"\nScreening for potential duplicate samples with up to {self.thresh} mismatching loci.")
		print("This can take a while with large files...\n")
		# find all unique pairs of indices
		rowPairs = list(combinations(range(len(self.npArr)), 2))

		# calculate mismatches for each pair and store result with indices
		results = []
		for i, j in rowPairs:
			mismatches = numpy.sum((self.npArr[i] != self.npArr[j]) & (self.npArr[i] == self.npArr[i]) & (self.npArr[j] == self.npArr[j])) # works to exclude nan values because expression 'a == a' evaluates to 'false' if a is nan
			if mismatches <= self.thresh:
				self.first.append(self.origIndex[i])
				self.second.append(self.origIndex[j])
				results.append((self.origIndex[i], self.origIndex[j], str(int(mismatches))))

		# Print the pairs with up to self.thresh mismatches
		print("These were detected as possible duplicates:") #stdout
		print("Sample_1\tSample_2\tMismatches") #stdout
		with open(self.log, 'a') as fh:
			fh.write("\nThese were detected as possible duplicates:\n") #log file
			fh.write("Sample_1\tSample_2\tMismatches\n") #log file
			for l in results:
				newString = '\t'.join(l)
				print(newString)
				fh.write(newString)
				fh.write("\n")
		
	def removeDups(self):
		removeList = list()
		if self.keep == "all":
			print("\nIf duplicates were detected, then all were retained.")
		elif self.keep == "first":
			print("\nFirst duplicate retained.")
			removeList = list(dict.fromkeys(self.second)) # remove second duplicate
		elif self.keep == "second":
			print("\nSecond duplicate retained.")
			removeList = list(dict.fromkeys(self.first)) # remove first duplicate
		elif self.keep == "none":
			print("\nNo duplicates retained.")
			allList = self.first + self.second # combine lists of first and second duplicates
			allList = sorted(allList) # sort list
			removeList = list(dict.fromkeys(allList)) # remove all duplicates
		else:
			print("This code should be unreachable.")
			print("No method for removing duplicates - how did you get here?")

		if removeList:
			print("The following samples are removed as duplicates:") #stdout
			with open(self.log, 'a') as fh:
				fh.write("\nThe following samples are removed as duplicates:\n") #log file
				for sample in removeList:
					print(sample) #stdout
					fh.write(sample) #log file
					fh.write("\n") #log file
				print("")
				fh.write("\n")

		return removeList
