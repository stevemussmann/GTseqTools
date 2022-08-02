from newhybrids import NewHybrids
from structure import Structure
from genepop import Genepop

class GTconvert():
	'Class for converting pandas dataframes into various genotype files'

	def __init__(self, pdf, popdata, struBool):
		self.structureTwoLine = struBool
		self.df = pdf
		self.pd = popdata

	def convert(self, d):
		for filetype, boolean in d.items():
			if boolean == True:
				self.convert_to(filetype)
		
	def conv_newhybrids(self):
		nh = NewHybrids(self.df)
		output = nh.convert()
		for line in output:
			print(line)
		#return output

	def conv_structure(self):
		print("This function will convert to Structure format.")
		stru = Structure(self.df, self.pd)
		stru.convert(self.structureTwoLine)

	def conv_genepop(self):
		print("This function will convert to Genepop format.")
		gen = Genepop(self.df)
		gen.convert()

	def convert_to(self, name: str):
		conv = f"conv_{name}"
		if hasattr(self, conv) and callable(func := getattr(self, conv)):
			func()
		else:
			print("Function not found for converting", name, "format.")
			print("Exiting program...")
			print("")
			raise SystemExit(1)
