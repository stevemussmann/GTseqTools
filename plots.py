import holoviews
import matplotlib.pyplot
import os
import pandas
import scipy

holoviews.extension('bokeh')

class GTPlots():
	'Class for generating summary plots'
	
	def __init__(self, d1, d2=None):
		self.d1 = d1 # ind dict for Sankey plots; sole dict for histogram and qq plots
		self.d2 = d2 # locus dict for Sankey plots; not used for histogram and qq plots
		self.plotDir = "plots"

	def printHistogram(self, fn, maxX, nBin, plotTitle, xAxisLabel):
		matplotlib.pyplot.figure().clear()
		dataSeries = pandas.Series(self.d1) # convert to pandas series
		dataSeries = pandas.to_numeric(dataSeries) # make sure data are numeric

		histo = dataSeries.plot.hist(grid=False, bins=nBin, range=(0.0, maxX), rwidth=0.9, color='#607c8e')
		histo.set_xlim(0.0, maxX)
		fig = histo.get_figure()

		matplotlib.pyplot.title(plotTitle)
		matplotlib.pyplot.xlabel(xAxisLabel)
		matplotlib.pyplot.ylabel('Counts')
		fig.savefig(fn, dpi=600)

	def printQQplot(self, qqFN, plotTitle, yAxisLabel):
		matplotlib.pyplot.figure().clear()
		matplotlib.pyplot.figure(figsize=(6,6))
		dfloat = {k: float(v) for k, v in self.d1.items()} # cast as floats because scipy doesn't like Decimal objects
		vallist = list(dfloat.values())
		res = scipy.stats.probplot(vallist, dist="norm", plot=matplotlib.pyplot)

		matplotlib.pyplot.title(plotTitle, fontsize=14)
		matplotlib.pyplot.xlabel("Theoretical Quantiles", fontsize=12)
		matplotlib.pyplot.ylabel(yAxisLabel, fontsize=12)
		matplotlib.pyplot.grid(True, linestyle="--", alpha=0.6)
		matplotlib.pyplot.savefig(qqFN, dpi=600, bbox_inches="tight")

	def printSankey(self, pdf):
		print("Writing sankey diagrams...")

		if self.d2 is None:
			print("Second dict (locus dict) not specified.")

		## individuals
		sankeyIndDF = pandas.DataFrame(self.d1) # convert sankey data to pandas dataframe
		sankeyIndDF['Count'] = pandas.to_numeric(sankeyIndDF['Count'], errors='coerce') # force count data to be numeric
		discardSum = sankeyIndDF.loc[sankeyIndDF['Source'] == 'Discarded', 'Count'].sum() # sum discarded values
		sankeyIndDF.loc[len(sankeyIndDF)] = ['All', 'Discarded', discardSum] # add discarded value sum to dataframe
		#print(sankeyIndDF, "\n")

		## loci
		self.d2["Source"].append("All")
		self.d2["Filter"].append("Retained")
		self.d2["Count"].append(len(pdf.columns))
		sankeyLocDF = pandas.DataFrame(self.d2)
		sankeyLocDF['Count'] = pandas.to_numeric(sankeyLocDF['Count'], errors='coerce') # force count data to be numeric
		discardSumLoc = sankeyLocDF.loc[sankeyLocDF['Source'] == 'Discarded', 'Count'].sum() # sum discarded values
		sankeyLocDF.loc[len(sankeyLocDF)] = ['All', 'Discarded', discardSumLoc] # add discarded value sum to dataframe
		#print(sankeyLocDF, "\n")

		sankeyInd = holoviews.Sankey(sankeyIndDF, label='Individuals') # make sankey object
		spInd = sankeyInd.opts(label_position='left', edge_color='Filter', node_color='index', cmap='tab20') # make sankey plot
		sankeyIndPath = os.path.join(self.plotDir, "sankey_plot_individuals.html") # make path for sankey output
		holoviews.save(spInd, sankeyIndPath, fmt="html") # print sankey plot - opted for html because .png and .svg options have too many dependencies
		print("Sankey diagram for individuals written to", str(sankeyIndPath))

		sankeyLoc = holoviews.Sankey(sankeyLocDF, label='Loci') # make sankey object
		spLoc = sankeyLoc.opts(label_position='left', edge_color='Filter', node_color='index', cmap='tab20') # make sankey plot
		sankeyLocPath = os.path.join(self.plotDir, "sankey_plot_loci.html") # make path for sankey output
		holoviews.save(spLoc, sankeyLocPath, fmt="html") # print sankey plot - opted for html because .png and .svg options have too many dependencies
		print("Sankey diagram for loci written to", str(sankeyLocPath), "\n")
	
