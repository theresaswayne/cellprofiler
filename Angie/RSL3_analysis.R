
# RSL3_analysis.R

# load your dataset...

cyt_intens <- X2019_03_01_Cytoplasm %>% group_by(Metadata_Treatment) %>% summarise(mean = mean(Intensity_MeanIntensity_Red), intden = mean(Intensity_IntegratedIntensity_Red))
