import argparse
import os.path
import distutils.util

class ComLine():
	'Class for implementing command line options'


	def __init__(self, args):
		parser = argparse.ArgumentParser()
		parser._action_groups.pop()
		required = parser.add_argument_group('required arguments')
		optional = parser.add_argument_group('optional arguments')
		conversion = parser.add_argument_group('conversion arguments')
		required.add_argument("-x", "--xlsx",
							dest='xlsx',
							required=True,
							help="Specify an Excel file in xlsx format for input."
		)
		optional.add_argument("-s", "--species",
							dest='species',
							help="Specify a list of loci that are species identification SNPs."
		)
		optional.add_argument("-i", "--pmissind",
							dest='pmissind',
							type=float,
							default=0.2,
							help="Enter the maximum allowable proportion of missing data for an individual (default = 0.2)."
		)
		optional.add_argument("-l", "--pmissloc",
							dest='pmissloc',
							type=float,
							default=0.1,
							help="Enter the maximum allowable proportion of missing data for a locus (default = 0.1)."
		)
		optional.add_argument("-t", "--twoline",
							dest='twoline',
							action='store_true',
							help="Turn on twoline format version for Structure output"
		)
		conversion.add_argument("-g", "--genepop",
							dest='genepop',
							action='store_true',
							help="Write genepop format file."
		)
		conversion.add_argument("-n", "--newhybrids",
							dest='newhybrids',
							action='store_true',
							help="Write NewHybrids format file."
		)
		conversion.add_argument("-S", "--structure",
							dest='structure',
							action='store_true',
							help="Write Structure format file."
		)
		self.args = parser.parse_args()

		print(self.args)

		#check if files exist
		#self.exists( self.args.popmap )
		self.exists( self.args.xlsx )
		if self.args.species:
			self.exists(self.args.species)

	def exists(self, filename):
		if( os.path.isfile(filename) != True ):
			print(filename, "does not exist")
			print("Exiting program...")
			print("")
			raise SystemExit
