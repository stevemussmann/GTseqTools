from decimal import *

import math
import numpy
import scipy

class GTStats():
	'Class for calculating summary statistics'
	
	def __init__(self):
		self.l = list()
		self.mean = 0.0
		self.stdev = 0.0
		self.med = 0.0
		self.mmin = 0.0
		self.mmax = 0.0

	def calcStats(self, l):
		self.l = l
		if len(self.l)!=0:
			self.mean = self.calcMean(self.l)
			self.stdev = self.calcStdev(self.l, self.mean)
			self.med = self.calcMed(self.l)
			self.mmin = min(self.l)
			self.mmax = max(self.l)
		
	def calcMean(self,l):
		total = self.calcSum(l)
		mean = (total/len(l))
		return mean

	def calcSum(self, l):
		total = Decimal()
		for item in l:
			total+=item
		return total

	def calcStdev(self, l, mean):
		vals = list()
		for val in l:
			dev = (val-mean)**2
			vals.append(dev)
		total = self.calcSum(vals)
		if len(l)-1 == 0:
			return 0
		else:
			temp = total/Decimal((len(l)-1))
			stdev = Decimal(math.sqrt(temp))
			return stdev

	def calcMed(self,l):
		sl = sorted(l)
		llen = len(l)
		i = (llen-1) // 2

		if(llen % 2):
			return sl[i]
		else:
			return Decimal((sl[i] + sl[i+1])/Decimal(2))

	def printStats(self, fn, mode1, mode2):
		if mode1 == "ifi scores":
			print(f"IFI score summary for {mode2} individuals:")
		elif mode1 == "heterozygosity":
			prepost = mode2.capitalize()
			print(f"{prepost} heterozygosity summary for individuals:")
		else:
			print(f"Proportion of missing data summary for {mode1} {mode2}:")
		print("Mean\tStDev\tMedian\tMin\tMax")

		fh = open(fn, 'a')
		if mode1 == "ifi scores":
			fh.write("IFI score stats for " + str(len(self.l)) + " individuals " + mode2 + ":\n")
		else:
			fh.write(str(len(self.l)) + " " + mode2 + " were detected " + mode1 + ".\n")
			fh.write("Missing data stats for " + mode1 + " " + mode2 + ":\n")

		fh.write("Mean\tStDev\tMedian\tMin\tMax\n")
		print(round(self.mean,3), "\t", round(self.stdev,3), "\t", round(self.med,3), "\t", round(self.mmin,3), "\t", round(self.mmax,3), "\n")
		fh.write(str(round(self.mean,3)) + "\t" + str(round(self.stdev,3)) + "\t" + str(round(self.med,3)) + "\t" + str(round(self.mmin,3)) + "\t" + str(round(self.mmax,3)) + "\n\n")
		
		fh.close()

	def chisq(self, start, end, fn):
		fh = open( fn, 'a')

		totalIn = start.sum() # total samples input
		totalOut = end.total() # total samples output
		pctRetained = float(totalOut / totalIn) # percentage of retained individuals

		obsList = list()
		expList = list()
		for k,v in start.items():
			if k in end:
				exp = self.expected(start[k], pctRetained)
				print("{}\t{}\t{}\t{}".format(k, v, end[k], "{:.2f}".format(exp)))
				fh.write(str(k) + "\t" + str(v) + "\t" + str(end[k]) + "\t" + "{:.2f}".format(exp) + "\n")
				obsList.append(float(end[k]))
				expList.append(float(exp))
			else:
				exp = self.expected(start[k], pctRetained)
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

		fh.close()

	def expected(self, inInds, pctRet):
		exp = inInds * pctRet

		return exp
