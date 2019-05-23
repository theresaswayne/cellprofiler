# Li_nuclear_intensity.R
# R script by Theresa Swayne

# Processes CellProfiler data on immunostaining

# Setup -------
require(tidyverse) # for reading and parsing
require(tcltk) # for file choosing
require(ggplot2) # for graphs

# Get data -----

datafile <- tk_choose.files(default = "", caption = "Select the CSV with Nuclei values", multi = FALSE) # file chooser window, with a message

df <- read_csv(datafile)

# Group by well

df <- df %>% group_by(Well = Metadata_Well)

# Threshold for Green to be considered positive
# in a 16-bit image 10000 = 0.152, 15000 = 0.22, 20000 = 0.30
green_thresh <- 0.22 # scale of 0 to 1

# display distribution in a violin plot

# violin scale:  if "area" (default), all violins have the same area (before trimming the tails). If "count", areas are scaled proportionally to the number of observations. If "width", all violins have the same maximum width.


plotAll <- ggplot(df, aes(factor(Well), Intensity_MeanIntensity_Green)) +
  geom_violin(scale = "area", draw_quantiles = 0.5) +
  labs(title =  "All detected cells",
       x = "Well", y = "Nuclear Mean Intensity, Alexa 488")

plotGreenHigh <- ggplot(df %>% filter(Intensity_MeanIntensity_Green >= green_thresh), 
                       aes(factor(Metadata_Well), Intensity_MeanIntensity_Green)) +
  geom_violin(scale = "area", draw_quantiles = 0.5) +
  labs(title =  paste("Cells with green intensity >= ",green_thresh),
       x = "Well", y = "Nuclear Mean Intensity, Alexa 488")

# mean Green in each well
green_mean <- df %>% summarise(Mean488 = mean(Intensity_MeanIntensity_Green))

# % of cells with green 
green_pct <- df %>% summarise(TotalCells = n(), FractionPositive = mean(Intensity_MeanIntensity_Green >= green_thresh))

# save plot and data tables

# saves the data one level up 
parentName <- basename(dirname(datafile)) # parent directory without higher levels
parentDir <- dirname(datafile)

green_meanFile = paste(Sys.Date(), parentName, "green_mean.csv") # spaces will be inserted
green_pctFile = paste(Sys.Date(), parentName, "Cells_over_",green_thresh,".csv") # spaces will be inserted

write_csv(green_mean,file.path(parentDir, green_meanFile))
write_csv(green_pct,file.path(parentDir, green_pctFile))

ggsave(plot = plotAll, filename = file.path(parentDir, paste(Sys.Date(), parentName, "_AllCells.png")))

ggsave(plot = plotGreenHigh, filename = file.path(parentDir, paste(Sys.Date(), parentName, "_Cells_over_",green_thresh,".png")))

