from popmap import Popmap

import os
import pandas

class Rubias():
	'Class for converting pandas dataframe to rubias format'

	def __init__(self, df, popmap, convDir):
		self.pdf = df
		self.pops = popmap
		self.nucleotides = {'A': '01', 'C': '02', 'G': '03', 'T': '04', '-': '05', '0': '00'}
		self.convertedDir = convDir
		
	def convert(self):
		pm = Popmap(self.pops)
		mapDict = pm.parseMap()

		print("Printing from inside rubias convert function.")

		lineList = list()

		# make header line
		for (columnName, columnData) in self.pdf.items():
			lineList.append(columnName)


		return lineList

	def split(self, word):
		return [char for char in word]
