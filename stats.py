from decimal import *

import math

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
