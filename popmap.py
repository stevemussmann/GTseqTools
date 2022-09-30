import pandas

class Popmap():
	'Class for parsing popmap data from a pandas dataframe'

	def __init__(self, popmap):
		self.pops = popmap

	def parseMap(self):
		mapDict = dict()
		for k,v in self.pops.items():
			self.pops[k] = str(v).strip().replace(" ", "_") #strip() removes leading and trailing whitespace
		s = set(self.pops.values()) #reduce to unique values
		counter=1
		for i in s:
			mapDict[str(i)] = counter #assign unique population number
			counter+=1

		return mapDict

	def printMap(self, mapDict):
		structurePops = list()
		for k,v in mapDict.items():
			line = list()
			line.append(str(v))
			line.append(k)
			lineString = '\t'.join(line)
			structurePops.append(lineString)

		return structurePops
			
			
