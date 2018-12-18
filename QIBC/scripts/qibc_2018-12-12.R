# load packages if not already loaded
require(dplyr)
require(readr)
require(ggplot2)
require(here)

# read data
all_objects <- read_csv(here("data", "2018-12-12_qibcC1DNANuclei.csv"))
hist(all_objects$AreaShape_Area)
# hist(all_objects$Intensity_IntegratedIntensity_Channel1DNACorr)
hist(all_objects$Intensity_IntegratedIntensity_Channel1DNACorr, breaks = (0:100))

# pull out data by genotype
AtrWT <- all_objects %>% filter(Metadata_basename == "Atr WT")
AtrKD <- all_objects %>% filter(Metadata_basename == "Atr KD")
AtrNull <- all_objects %>% filter(Metadata_basename == "Atr-")

# DNA content
hist(AtrWT$Intensity_IntegratedIntensity_Channel1DNACorr, breaks= (0:100), main = "WT DNA Content")
hist(AtrKD$Intensity_IntegratedIntensity_Channel1DNACorr, breaks= (0:100), main = "Atr KD DNA Content")
hist(AtrNull$Intensity_IntegratedIntensity_Channel1DNACorr, breaks= (0:100), main = "Atr- DNA Content")

# Area of detected objects
hist(AtrWT$AreaShape_Area)
hist(AtrKD$AreaShape_Area)
hist(AtrNull$AreaShape_Area)
#cat(mean(all_objects$AreaShape_FormFactor < 0.5)) # how many objects are not roundish?

# build a scatter plot of DNA content vs EdU

# 
# p <- ggplot(AtrWT,
#             aes(AtrWT$Intensity_IntegratedIntensity_Channel1DNACorr, AtrWT$Intensity_MeanIntensity_Channel2EdUCorr)) +
#     geom_point() +
#     scale_y_log10()
# 
# TODO: M