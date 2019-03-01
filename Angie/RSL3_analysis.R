
# RSL3_analysis.R

# load your dataset...

require(tidyverse)
require(tcltk)


cyt_data <- tk_choose.files(caption = "Select Cytoplasm measurements") %>% 
  read.csv
memb_data <- tk_choose.files(caption = "Select Membrane measurements") %>% 
  read.csv


cyt_intens <- cyt_data %>% 
  group_by(Metadata_Treatment) %>% 
  summarise(Cyto_Mean = mean(Intensity_MeanIntensity_Red),
            Cyto_IntDen = mean(Intensity_IntegratedIntensity_Red))

memb_intens <- memb_data %>% 
  group_by(Metadata_Treatment) %>% 
  summarise(Memb_Mean = mean(Intensity_MeanIntensity_Red),
            Memb_IntdDen = mean(Intensity_IntegratedIntensity_Red),
            Total_Memb_Area = sum(AreaShape_Area))

merged_intens <- left_join(cyt_intens, memb_intens)

write.csv(merged_intens, file = "Results.csv") # in the project directory

