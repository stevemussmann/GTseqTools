import argparse
import os.path
#import distutils.util

class ComLine():
	'Class for implementing command line options'


	def __init__(self, args):
		parser = argparse.ArgumentParser()
		parser._action_groups.pop()
		required = parser.add_argument_group('required arguments')
		filtering = parser.add_argument_group('filtering arguments')
		optional = parser.add_argument_group('optional arguments')
		conversion = parser.add_argument_group('conversion arguments')
		colony = parser.add_argument_group('colony format arguments')
		structure = parser.add_argument_group('structure format arguments')
		snppit = parser.add_argument_group('snppit format arguments')
		required.add_argument("-x", "--infile",
							dest='infile',
							required=True,
							help="Specify an Excel file in xlsx format for input."
		)
		filtering.add_argument("-D", "--dups",
							dest='dups',
							action='store_true',
							help="Detect duplicate genotypes (can take a while on large files; default = False)."
		)
		filtering.add_argument("-i", "--pmissind",
							dest='pmissind',
							type=float,
							default=0.2,
							help="Enter the maximum allowable proportion of missing data for an individual (default = 0.2)."
		)
		filtering.add_argument("-I", "--ifi",
							dest='ifi',
							type=float,
							default=2.5,
							help="Enter the maximum allowable IFI score for a genotype (default = 2.5)."
		)
		filtering.add_argument("-k", "--keepdups",
							dest='keepdups',
							type=str,
							default='none',
							choices={'all','first','second','none'},
							help="Methods for keeping duplicates. 'all' = keep all duplicates; 'first' = keep first encountered; 'second' = keep second; 'none' = keep none (default)"
		)
		filtering.add_argument("-l", "--pmissloc",
							dest='pmissloc',
							type=float,
							default=0.1,
							help="Enter the maximum allowable proportion of missing data for a locus (default = 0.1)."
		)
		filtering.add_argument("-m", "--monomorphic",
							dest='monomorphic',
							action='store_true',
							help="Turn on filter to remove monomorphic loci."
		)
		filtering.add_argument("-r", "--removeinds",
							dest='removeinds',
							help="Specify a list of individuals to remove from the converted files."
		)
		filtering.add_argument("-R", "--removeloci",
							dest='removeloci',
							help="Specify a list of individuals to remove from the converted files."
		)
		filtering.add_argument("-T", "--dupthresh",
							dest='dupthresh',
							type=int,
							default=3,
							help="Maximum number of allelic mismatches for identifying duplicate individuals (default = 3)."
		)
		optional.add_argument("-d", "--sexid",
							dest='sexid',
							help="Specify a list of loci that are sex-identifying SNPs."
		)
		optional.add_argument("-P", "--keeppops",
							dest='keeppops',
							help="Provide a text file of populations to retain. One population per line. Populations must match data in 'Population ID' column of your input Excel file."
		)
		optional.add_argument("-s", "--species",
							dest='species',
							help="Specify a list of loci that are species identification SNPs."
		)
		colony.add_argument("-B", "--inbreed",
							dest='inbreed',
							type=int,
							default=0,
							choices={0,1},
							help="0 = inbreeding absent; 1 = inbreeding present (default = 0)."
		)
		colony.add_argument("-e", "--droperr",
							dest='droperr',
							type=float,
							default=0.0005,
							help="Enter the assumed allelic dropout rate (default = 0.0005)."
		)
		colony.add_argument("-E", "--genoerr",
							dest='genoerr',
							type=float,
							default=0.0005,
							help="Enter the assumed genotyping error rate (default = 0.0005)."
		)
#		colony.add_argument("-e", "--genoerrfile", ## NEED TO USE DIFFERENT LETTER
#							dest='genoerrfile',
#							help='Specify a list of marker-specific genotyping error rates (optional).'
#		)
		colony.add_argument("-L", "--runlength",
							dest='runlength',
							type=int,
							default=2,
							choices={1,2,3,4},
							help="1/2/3/4 = Short/Medium/Long/VeryLong run (default = 2)."
		)
		colony.add_argument("-M", "--pmale",
							dest='pmale',
							type=float,
							default=0.5,
							help="Enter the assumed probability of father being among candidate parents (default = 0.5). Value is ignored if no candidate fathers provided in the dataset."
		)
		colony.add_argument("-F", "--pfemale",
							dest='pfemale',
							type=float,
							default=0.5,
							help="Enter the assumed probability of mother being among candidate parents (default = 0.5). Value is ignored if no candidate mothers provided in the dataset."
		)
		structure.add_argument("-t", "--twoline",
							dest='twoline',
							action='store_true',
							help="Turn on twoline format version for Structure output"
		)
		structure.add_argument("-H", "--header",
							dest='header',
							action='store_false',
							help="Turn off printing of header line with locus names for Structure output"
		)
		conversion.add_argument("-a", "--allelematch",
							dest='allelematch',
							action='store_true',
							help="Write allelematch format file."
		)
		conversion.add_argument("-b", "--binary",
							dest='binary',
							action='store_true',
							help="Write binary format file."
		)
		conversion.add_argument("-c", "--coancestry",
							dest='coancestry',
							action='store_true',
							help="Write coancestry format file."
		)
		conversion.add_argument("-C", "--colony",
							dest='colony',
							action='store_true',
							help="Write colony format file."
		)
		conversion.add_argument("-g", "--genepop",
							dest='genepop',
							action='store_true',
							help="Write genepop format file."
		)
		conversion.add_argument("-G", "--grandma",
							dest='grandma',
							action='store_true',
							help="Write gRandma format file."
		)
		conversion.add_argument("-n", "--newhybrids",
							dest='newhybrids',
							action='store_true',
							help="Write NewHybrids format file."
		)
		conversion.add_argument("-p", "--plink",
							dest='plink',
							action='store_true',
							help="Write Plink format file."
		)
		conversion.add_argument("-q", "--sequoia",
							dest='sequoia',
							action='store_true',
							help="Write Sequoia format file."
		)
		conversion.add_argument("-S", "--structure",
							dest='structure',
							action='store_true',
							help="Write Structure format file."
		)
		conversion.add_argument("-X", "--xlsx",
							dest='xlsx',
							action='store_true',
							help="Write filtered Excel format file."
		)
		conversion.add_argument("-z", "--snppit",
							dest='snppit',
							action='store_true',
							help="Write SNPPIT format file."
		)
		snppit.add_argument("-Z", "--snppitmap",
							dest='snppitmap',
							help="Provide a tab-delimited file specifying POP and OFFSPRING groups for SNPPIT format. Required if converting a SNPPIT file."
		)
		self.args = parser.parse_args()

		#check if at least one conversion option was used.
		if not [x for x in (self.args.allelematch, self.args.binary, self.args.coancestry, self.args.colony, self.args.genepop, self.args.grandma, self.args.newhybrids, self.args.plink, self.args.sequoia, self.args.structure, self.args.snppit, self.args.xlsx) if x is True]:
			print("")
			print("No format conversion options were selected.")
			print("You must choose at least one file format for output.")
			print("")
			raise SystemExit

		#check if input file ends with .xlsx
		if not self.args.infile.endswith(".xlsx"):
			print("ERROR: Input file " + self.args.infile + " does not end with .xlsx file extension.")
			print("Is this a valid excel file?")
			print("Exiting Program...")
			print("")
			raise SystemExit

		#check if files exist
		self.exists( self.args.infile )
		if self.args.species:
			self.exists(self.args.species)
		if self.args.sexid:
			self.exists(self.args.sexid)
		if self.args.removeinds:
			self.exists(self.args.removeinds)
		if self.args.removeloci:
			self.exists(self.args.removeloci)
		if self.args.keeppops:
			self.exists(self.args.keeppops)
		if self.args.snppit == True:
			if self.args.snppitmap is None:
				print("")
				print("If doing a snppit conversion you must also specify a POP and OFFSPRING groups file using the -Z option.")
				print("")
				raise SystemExit
			else:
				self.exists(self.args.snppitmap)


	def exists(self, filename):
		if( os.path.isfile(filename) != True ):
			print("")
			print(filename, "does not exist")
			print("Exiting program...")
			print("")
			raise SystemExit
