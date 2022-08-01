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
		#required.add_argument("-m", "--popmap",
		#					dest='popmap',
		#					required=True,
		#					help="Specify a tab-delimited population map (sample -> population)"
		#)
		required.add_argument("-x", "--xlsx",
							dest='xlsx',
							required=True,
							help="Specify an Excel file in xlsx format for input."
		)
		optional.add_argument("-s", "--species",
							dest='species',
							help="Specify a list of loci that are species identification SNPs."
		)
		#opt_admix.add_argument("-k", "--minK",
		#					dest='minK',
		#					type=int,
		#					default=1,
		#					help="minimum K value."
		#)
		#opt_admix.add_argument("-K", "--maxK",
		#					dest='maxK',
		#					type=int,
		#					default=20,
		#					help="maximum K value."
		#)
		#opt_vcf.add_argument("-M", "--mac",
		#			dest='mac',
		#			type=int,
		#			default=0,
		#			help="Enter the minimum count for the minor allele filter."
		#)

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
		#opt_vcf.add_argument("-t", "--thin",
		#					dest='thin',
		#					type=int,
		#					default=0,
		#					help="Use VCFtools to thin out loci falling within the specified proximity to one another."
		#)
		#opt_vcf.add_argument("-r", "--remove",
		#					dest='remove',
		#					help="Specify a file of blacklisted individuals to have VCFtools remove from the analysis."
		#)
		#opt_vcf.add_argument("-C", "--indcov",
		#					dest='indcov',
		#					type=float,
		#					default=0.9,
		#					help="Specify the maximum allowable missing data per individual"
		#)
		#opt_vcf.add_argument("-S", "--snpcov",
		#					dest='snpcov',
		#					type=float,
		#					default=0.1,
		#					help="Specify the allowable proportion of missing data per SNP. 0 allows sites that are completely missing and 1 indicates no missing data allowed."
		#)
		#opt_admix.add_argument("-c", "--cv",
		#					dest='cv',
		#					type=int,
		#					default=20,
		#					help="Specify the cross-validation number for admixture program"
		#)
		#opt_admix.add_argument("-R", "--rep",
		#					dest='rep',
		#					type=int,
		#					default=20,
		#					help="Number of replicates per K."
		#)
		#opt_vcf.add_argument("-b", "--bi",
		#					dest='bi',
		#					action='store_true',
		#					help="Turn off filter for biallelic SNPs."
		#)

		self.args = parser.parse_args()

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
