# qbic_illum_comp.R
# comparing tiff and npy illumination correction

# load packages if not already loaded
require(dplyr)
require(readr)
require(ggplot2)
require(here)

# load data that you have placed in the data folder
qbic_tiff <- read_csv(here("data", "2018-11-05 data 2018-12-06 tiff illum corr/2018-12-06_qbic_C1DNANuclei.csv"))
qbic_npy <- read_csv(here("data", "2018-11-05 data 2018-12-12 npy illum corr/2018-12-12_qbic_npy_corrC1DNANuclei.csv"))

# get relevant data columns
dnaTotalInt_tiff <- qbic_tiff$Intensity_IntegratedIntensity_Channel1DNACorr
EdUMeanInt_tiff <- qbic_tiff$Intensity_MeanIntensity_Channel2EdUCorr
gH2AXMeanInt_tiff <- qbic_tiff$Intensity_MeanIntensity_Channel3gH2AXCorr

dnaTotalInt_npy <- qbic_npy$Intensity_IntegratedIntensity_Channel1DNACorr
EdUMeanInt_npy <- qbic_npy$Intensity_MeanIntensity_Channel2EdUCorr
gH2AXMeanInt_npy <- qbic_npy$Intensity_MeanIntensity_Channel3gH2AXCorr

# compare histograms
max_range <- max(range(dnaTotalInt_npy)[2], range(dnaTotalInt_tiff)[2])
par(mfrow = c(1,1))
hist(dnaTotalInt_tiff, xlim=c(0,max_range), breaks = (0:50), col= rgb (1,0,0,0.5), main = "TIFF corrected") # more breaks than default, to show detail
# hist(dnaTotalInt_npy,xlim=c(0,max_range),breaks=(0:50),col=rgb(0,1,1,0),main="",xlab="boo",ylab="", add = T) # add to previous plot

hist(dnaTotalInt_npy,xlim=c(0,max_range),breaks=(0:50),col=rgb(0,1,0,0.5),main="NPY corrected")

# see also https://stackoverflow.com/questions/3541713/how-to-plot-two-histograms-together-in-r (ggplot)
# see also https://www.r-bloggers.com/overlapping-histogram-in-r/ (base plot)

plot(x = dnaTotalInt_tiff, y = EdUMeanInt_tiff, log = "y", main = "Tiff correction, Mean EdU (log) vs Total DNA") # scatter plot with log Y axis
plot(x = dnaTotalInt_npy, y = EdUMeanInt_npy, log = "y", main = "NPY correction, Mean EdU (log) vs Total DNA") # scatter plot with log Y axis

plot(x = dnaTotalInt_tiff, y = gH2AXMeanInt_tiff, log = "y", main = "Tiff correction, Mean EdU (log) vs Total DNA") # scatter plot with log Y axis
plot(x = dnaTotalInt_npy, y = gH2AXMeanInt_npy, log = "y", main = "NPY correction, Mean EdU (log) vs Total DNA") # scatter plot with log Y axis

