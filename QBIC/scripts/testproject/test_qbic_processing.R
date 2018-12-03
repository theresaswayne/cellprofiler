# test_qbic_processing.R
# for examining CellProfiler data from nuclear analyses
# adapting to project-based structure

# load packages
#library(dplyr)
#library(readr)
#library(ggplot2)
#library(here)

require(dplyr)
require(readr)
require(ggplot2)
require(here)

# load data which you have placed in the data folder

qbic_C1DNANuclei <- read_csv(here("data", "qbic_C1DNANuclei.csv"))
dnaTotalInt <- qbic_C1DNANuclei$Intensity_IntegratedIntensity_Channel1DNACorr
EdUMeanInt <- qbic_C1DNANuclei$Intensity_MeanIntensity_Channel2EdUCorr
p <- ggplot(qbic_C1DNANuclei, aes(dnaTotalInt, EdUMeanInt)) + geom_point()
ggsave(here("results", "foofy_scatterplot.png"))


hist(dnaTotalInt, main = "Test 2")
hist(dnaTotalInt, breaks = (0:50), main = "Test 2")


plot(x = dnaTotalInt, y = EdUMeanInt,main = "Test 2") # basic scatter plot

low_vals <- mean(dnaTotalInt < 1)
high_vals <- mean(dnaTotalInt > 30)
central_vals <- mean(dnaTotalInt > 1 & dnaTotalInt < 30)

cat(central_vals, "of the values are between 1 and 30; ",low_vals,"<1; and",high_vals,">30")

