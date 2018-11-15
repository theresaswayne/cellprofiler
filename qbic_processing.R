# qbic_processing.R
# for reading CellProfiler data from nuclear analyses

library(readr)
qbic_C1DNANuclei <- read_csv("~/Desktop/output/qbic_C1DNANuclei.csv")

#dnaTotalInt <- qbic_C1DNANuclei$Intensity_IntegratedIntensity_Channel1DNA
#EdUMeanInt <- qbic_C1DNANuclei$Intensity_MeanIntensity_Channel2EdU
dnaTotalInt <- qbic_C1DNANuclei$Intensity_IntegratedIntensity_Channel1DNACorr
EdUMeanInt <- qbic_C1DNANuclei$Intensity_MeanIntensity_Channel2EdUCorr

plot(x = dnaTotalInt, y = EdUMeanInt) # basic scatter plot

hist(dnaTotalInt)