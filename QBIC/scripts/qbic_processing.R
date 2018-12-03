# qbic_processing.R
# for examining CellProfiler data from nuclear analyses

library(dplyr)
library(readr)

qbic_C1DNANuclei <- read_csv("~/Desktop/output/qbic_C1DNANuclei.csv")

#dnaTotalInt <- qbic_C1DNANuclei$Intensity_IntegratedIntensity_Channel1DNA
#EdUMeanInt <- qbic_C1DNANuclei$Intensity_MeanIntensity_Channel2EdU
dnaTotalInt <- qbic_C1DNANuclei$Intensity_IntegratedIntensity_Channel1DNACorr
EdUMeanInt <- qbic_C1DNANuclei$Intensity_MeanIntensity_Channel2EdUCorr


hist(dnaTotalInt, main = "Test 2")
hist(dnaTotalInt, breaks = (0:50), main = "Test 2")


plot(x = dnaTotalInt, y = EdUMeanInt,main = "Test 2") # basic scatter plot

low_vals <- mean(dnaTotalInt < 1)
high_vals <- mean(dnaTotalInt > 30)
central_vals <- mean(dnaTotalInt > 1 & dnaTotalInt < 30)

cat(central_vals, "of the values are between 1 and 30; ",low_vals,"<1; and",high_vals,">30")

