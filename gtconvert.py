from newhybrids import NewHybrids
from structure import Structure
from genepop import Genepop
from snppit import Snppit
from plink import Plink

class GTconvert():
	'Class for converting pandas dataframes into various genotype files'

	def __init__(self, pdf, popdata, struBool, headBool, snppitmap, snppitCols, infile):
		self.structureTwoLine = struBool
		self.structureHeader = headBool
		self.snppitmap = snppitmap
		self.snppitCols = snppitCols
		self.df = pdf
		self.pd = popdata
		self.infile = infile
		self.suffix = {'genepop': 'gen', 'newhybrids': 'newhyb', 'plink': 'ped', 'structure': 'str', 'snppit': 'snppit'}

	def convert(self, d):
		output = list()
		for filetype, boolean in d.items():
			if boolean == True:
				print("Converting to", filetype, "format file.")
				output = self.convert_to(filetype)
				self.printOutput(output, self.infile, self.suffix[filetype])
		
	def conv_newhybrids(self):
		#print("This function will convert to NewHybrids format.")
		nh = NewHybrids(self.df)
		output = nh.convert()
		return output
	
	def conv_plink(self):
		#print("This function will convert to Plink format.")
		ped = Plink(self.df)
		output, plinkmap = ped.convert() #returning two lists because also must print plink map
		self.printOutput(plinkmap, self.infile, "map") #special call to print plink map
		return output

	def conv_structure(self):
		#print("This function will convert to Structure format.")
		stru = Structure(self.df, self.pd)
		output, structureMap = stru.convert(self.structureTwoLine, self.structureHeader)
		self.printOutput(structureMap, self.infile, "distructLabels.txt")
		return output

	def conv_genepop(self):
		#print("This function will convert to Genepop format.")
		gen = Genepop(self.df, self.pd)
		output = gen.convert()
		return output

	def conv_snppit(self):
		#print("This function will convert to SNPPIT format.")
		snppit = Snppit(self.df, self.pd)
		output = snppit.convert(self.snppitmap, self.snppitCols)
		return output

	def convert_to(self, name: str):
		conv = f"conv_{name}"
		output = list()
		if hasattr(self, conv) and callable(func := getattr(self, conv)):
			output = func()
		else:
			print("Function not found for converting", name, "format.")
			print("Exiting program...")
			print("")
			raise SystemExit(1)
		return output

	def printOutput(self, output, fileName, suffix):
		# make new file name for writing
		fileName = fileName.replace(" ", "_") #replace spaces in original filename if they exist
		nameList = fileName.split('.')
		nameList.pop() #remove old extension
		nameList.append(suffix) #add new file extension
		outName = '.'.join(nameList)

		print("Writing to", outName)
		print("")

		fh = open(outName, 'w')

		for line in output:
			fh.write(line)
			fh.write("\n")
