import pandas

class Genepop():
	'Class for converting pandas dataframe to Genepop format'

	def __init__(self, df):
		self.pdf = df
		self.nucleotides = {'A': '01', 'C': '02', 'G': '03', 'T': '04', '0': '00'}
		
	def convert(self):
		print("You reached the convert function in Genepop class")
