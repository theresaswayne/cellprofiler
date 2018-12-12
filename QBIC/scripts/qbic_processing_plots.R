# qbic_processing_plots.R
# for examining CellProfiler data from nuclear analyses

# load packages if not already loaded
require(dplyr)
require(readr)
require(ggplot2)
require(here)

# load data that you have placed in the data folder
qbic <- read_csv(here("data", "2018-11-05 data 2018-12-12 npy illum corr/2018-12-12_qbic_npy_corrC1DNANuclei.csv"))

# get relevant data columns
dnaTotalInt <- qbic$Intensity_IntegratedIntensity_Channel1DNACorr
EdUMeanInt <- qbic$Intensity_MeanIntensity_Channel2EdUCorr
gH2AXMeanInt <- qbic$Intensity_MeanIntensity_Channel3gH2AXCorr

# histogram of DNA content
xmax <- ceiling(range(dnaTotalInt)[2]) # range is a vector of 2 elements
hist(dnaTotalInt, xlim=c(0,xmax), breaks = (0:xmax), col= rgb (1,0,0,0.5), main = "DNA Total Intensity") # more breaks than default, to show detail

# TODO: ggplot histogram
# see https://stackoverflow.com/questions/3541713/how-to-plot-two-histograms-together-in-r (ggplot)

#hist(dnaTotalInt, main = "Histogram of DNA total intensity") # default breaks
# hist(dnaTotalInt, breaks = (0:50), main = "Histogram of DNA total intensity") # more breaks, to show detail

#plot(x = dnaTotalInt, y = EdUMeanInt, log = "y", main = "Mean EdU (log) vs Total DNA") # basic scatter plot with log Y axis
#plot(x = dnaTotalInt, y = EdUMeanInt,main = "Mean EdU vs Total DNA") # scatter plot with log Y axis

#p <- ggplot(qbic_C1DNANuclei, aes(dnaTotalInt, EdUMeanInt)) + geom_point()
#ggsave(here("reports", "foofy_scatterplot.png"))
