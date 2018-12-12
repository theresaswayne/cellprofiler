# qbic_processing.R
# for examining CellProfiler data from nuclear analyses

# load packages if not already loaded
require(dplyr)
require(readr)
require(ggplot2)
require(here)

# load data that you have placed in the data folder
qbic_C1DNANuclei <- read_csv(here("data", "2018-11-05 data 2018-12-06 tiff illum corr/2018-12-06_qbic_C1DNANuclei.csv"))

#dnaTotalInt <- qbic_C1DNANuclei$Intensity_IntegratedIntensity_Channel1DNA
#EdUMeanInt <- qbic_C1DNANuclei$Intensity_MeanIntensity_Channel2EdU
dnaTotalInt <- qbic_C1DNANuclei$Intensity_IntegratedIntensity_Channel1DNACorr
EdUMeanInt <- qbic_C1DNANuclei$Intensity_MeanIntensity_Channel2EdUCorr


hist(dnaTotalInt, main = "Histogram of DNA total intensity") # default breaks
hist(dnaTotalInt, breaks = (0:50), main = "Histogram of DNA total intensity") # more breaks, to show detail

plot(x = dnaTotalInt, y = EdUMeanInt, log = "y", main = "Mean EdU (log) vs Total DNA") # basic scatter plot with log Y axis
plot(x = dnaTotalInt, y = EdUMeanInt,main = "Mean EdU vs Total DNA") # scatter plot with log Y axis

p <- ggplot(qbic_C1DNANuclei, aes(dnaTotalInt, EdUMeanInt)) + geom_point()
ggsave(here("reports", "foofy_scatterplot.png"))

pct_low_vals <- mean(dnaTotalInt < 1) * 100
pct_high_vals <- mean(dnaTotalInt > 30) * 100
pct_central_vals <- mean(dnaTotalInt > 1 & dnaTotalInt < 30) *100

cat(pct_central_vals, "% of the values are between 1 and 30; ",pct_low_vals,"% < 1; and",pct_high_vals,"% > 30")

