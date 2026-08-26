	def makeHetPlot(self, d, fn):
		matplotlib.pyplot.figure().clear()
		hetSeries = pandas.Series(d)

		# get maximum IFI value
		maxHet = 1.0

		# give about 40 bins per 5.0 IFI score units
		binCount = 50

		hetSeries = pandas.to_numeric(hetSeries)
		histo = hetSeries.plot.hist(grid=False, bins=binCount, range=(0.0,maxHet), rwidth=0.9, color='#607c8e')
		histo.set_xlim(0.0, maxHet)
		fig = histo.get_figure()
		matplotlib.pyplot.title('Ho Value Distribution')
		matplotlib.pyplot.xlabel('Ho Values')
		matplotlib.pyplot.ylabel('Counts')
	
	def makeMismatchHisto(self, d, histoFN):
		matplotlib.pyplot.figure().clear()
		mismatchSeries = pandas.Series(d)

		# get maximum mismatch value
		maxMismatch = mismatchSeries.max()

		# Set number of bins to number of mismatches
		binCount = maxMismatch

		# histogram plot
		mismatchSeries = pandas.to_numeric(mismatchSeries)
		histo = mismatchSeries.plot.hist(grid=False, bins=binCount, range=(0.0,maxMismatch), rwidth=0.9, color='#607c8e')
		histo.set_xlim(0.0, maxMismatch)
		fig = histo.get_figure()
		matplotlib.pyplot.title('Distribution of Genotype Mismatches')
		matplotlib.pyplot.xlabel('Mismatches')
		matplotlib.pyplot.ylabel('Counts')

	def makeIFIplot(self, d, fn):
		matplotlib.pyplot.figure().clear()
		ifiSeries = pandas.Series(d)

		# get maximum IFI value
		maxIFI = ifiSeries.max()

		# give about 40 bins per 5.0 IFI score units
		binCount = int(maxIFI/0.125)

		ifiSeries = pandas.to_numeric(ifiSeries)
		histo = ifiSeries.plot.hist(grid=False, bins=binCount, range=(0.0,maxIFI), rwidth=0.9, color='#607c8e')
		histo.set_xlim(0.0, maxIFI)
		fig = histo.get_figure()
		matplotlib.pyplot.title('IFI Score Distribution')
		matplotlib.pyplot.xlabel('IFI Scores')
		matplotlib.pyplot.ylabel('Counts')

	def plotMissing(self, d, fn):
		matplotlib.pyplot.figure().clear()
		missSeries = pandas.Series(d)
		missSeries = pandas.to_numeric(missSeries)
		histo = missSeries.plot.hist(grid=False, bins=40, range=(0.0,1.0), rwidth=0.9, color='#607    c8e')
		histo.set_xlim(0.0, 1.0)
		fig = histo.get_figure()
		matplotlib.pyplot.title('Proportion of Missing GTseq Data')
		matplotlib.pyplot.xlabel('Proportion Missing')
		matplotlib.pyplot.ylabel('Counts')
		fig.savefig(fn, dpi=600)
