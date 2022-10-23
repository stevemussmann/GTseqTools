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

	def printMap(self, mapDict, pdf):
		poplist = list()

		#check which populations have members that survived all filtering steps
		for sampleName, row in pdf.iterrows():
			if sampleName in self.pops.keys():
				poplist.append(self.pops[sampleName])

		s = set(poplist) #get unique population values
			
		structurePops = list()
		for k,v in mapDict.items():
			#restrict distructLabels file to only populations present after filtering
			if k in s:
				line = list()
				line.append(str(v))
				line.append(k)
				lineString = '\t'.join(line)
				structurePops.append(lineString)

		return structurePops
			
			
