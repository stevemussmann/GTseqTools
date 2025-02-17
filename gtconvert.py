from allelematch import AlleleMatch
from binary import Binary
from coancestry import Coancestry
from genepop import Genepop
from grandma import gRandma
from newhybrids import NewHybrids
from plink import Plink
from sequoia import Sequoia
from snppit import Snppit
from structure import Structure

import os

class GTconvert():
	'Class for converting pandas dataframes into various genotype files'

	def __init__(self, pdf, popdata, struBool, headBool, snppitmap, snppitCols, newhybCols, infile, log):
		self.structureTwoLine = struBool
		self.structureHeader = headBool
		self.snppitmap = snppitmap
		self.snppitCols = snppitCols
		self.newhybCols = newhybCols
		self.df = pdf
		self.pd = popdata
		self.infile = infile
		self.log = log
		self.suffix = {'allelematch': 'allelematch', 'binary': 'bin', 'coancestry': 'coancestry', 'genepop': 'gen', 'grandma': 'grandma', 'newhybrids': 'newhyb', 'plink': 'ped', 'structure': 'str', 'snppit': 'snppit', 'sequoia': 'sequoia'}
		
		self.convertedDir = "convertedFiles"
		if os.path.exists(self.convertedDir) == False:
			os.mkdir(self.convertedDir)

	def convert(self, d):
		output = list()
		for filetype, boolean in d.items():
			if boolean == True:
				print("Converting to", filetype, "format file.")
				output = self.convert_to(filetype)
				self.printOutput(output, self.infile, self.suffix[filetype])
		
	def conv_allelematch(self):
		#print("This function will convert to allelematch format.")
		am = AlleleMatch(self.df, self.pd)
		output = am.convert()
		return output
	
	def conv_binary(self):
		#print("This function will convert to binary format.")
		bi = Binary(self.df, self.pd)
		output = bi.convert()
		return output
	
	def conv_coancestry(self):
		#print("This function will convert to coancestry format.")
		am = Coancestry(self.df, self.pd, self.convertedDir)
		output = am.convert()
		return output

	def conv_newhybrids(self):
		#print("This function will convert to NewHybrids format.")
		nh = NewHybrids(self.df, self.pd, self.convertedDir)
		output = nh.convert(self.newhybCols)
		return output
	
	def conv_plink(self):
		#print("This function will convert to Plink format.")
		ped = Plink(self.df)
		output, plinkmap = ped.convert() #returning two lists because also must print plink map
		self.printOutput(plinkmap, self.infile, "map") #special call to print plink map
		return output
	
	def conv_sequoia(self):
		#print("This function will convert to binary format.")
		seq = Sequoia(self.df, self.pd, self.convertedDir)
		output = seq.convert(self.snppitCols)
		return output

	def conv_structure(self):
		#print("This function will convert to Structure format.")
		stru = Structure(self.df, self.pd)
		output, structureMap = stru.convert(self.structureTwoLine, self.structureHeader)
		self.printOutput(structureMap, self.infile, "distructLabels.txt")
		return output

	def conv_genepop(self):
		#print("This function will convert to Genepop format.")
		gen = Genepop(self.df, self.pd, self.convertedDir)
		output = gen.convert()
		return output

	def conv_grandma(self):
		#print("This function will convert to gRandma format.")
		gma = gRandma(self.df, self.log, self.pd)
		output = gma.convert()
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
		outName = os.path.join(self.convertedDir, outName)

		print("Writing to", outName)
		print("")

		fh = open(outName, 'w')

		for line in output:
			fh.write(line)
			fh.write("\n")
