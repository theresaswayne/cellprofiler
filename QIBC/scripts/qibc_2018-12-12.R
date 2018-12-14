# load packages if not already loaded
require(dplyr)
require(readr)
require(ggplot2)

all_objects <- read_csv("/Volumes/TOSHIBA EXT/2018-12-12/output/2018-12-12_qibcC1DNANuclei.csv")
hist(all_objects$AreaShape_Area)
hist(all_objects$Intensity_IntegratedIntensity_Channel1DNACorr)

hist(all_objects$Intensity_IntegratedIntensity_Channel1DNACorr, breaks = (0:100))
AtrWT <- all_objects %>% filter(Metadata_basename == "Atr WT")
hist(AtrWT$Intensity_IntegratedIntensity_Channel1DNACorr, breaks= (0:100))
hist(AtrWT$AreaShape_Area)

p <- ggplot(AtrWT_DNA_above_thresh, 
            aes(AtrWT_DNA_above_thresh$Intensity_IntegratedIntensity_Channel1DNACorr, AtrWT_DNA_above_thresh$Intensity_MeanIntensity_Channel2EdUCorr)) + 
    geom_point() + 
    scale_y_log10()
mean(all_objects$AreaShape_FormFactor < 0.5)
