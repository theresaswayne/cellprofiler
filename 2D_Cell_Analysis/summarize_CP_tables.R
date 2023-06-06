# summarize_CP_tables.R
# R script to select mean and edge intensity data from CellProfiler object results files
# and summarize by experiment and well (designed for Cytation imager data)
# To use: Run the script.
# Will be prompted for a file

# ---- Setup ----
require(tidyverse)
require(readr)
require(stringr)


# ---- Prompt for an object file ----
# no message will be displayed
objectFile <- file.choose()

# Read the data from the file
objectData <- read_csv(objectFile,
                    locale = locale())


mean_intens <- objectData %>% 
  group_by(Metadata_Experiment, Metadata_Well) %>% 
  summarise(nCells = n(),
            Mean = mean(Intensity_MeanIntensity_Green),
            IntDen = mean(Intensity_IntegratedIntensity_Green))

edge_intens <- objectData %>% 
  group_by(Metadata_Experiment, Metadata_Well) %>% 
  summarise(Edge_Mean = mean(Intensity_MeanIntensityEdge_Green),
            Edge_IntDen = mean(Intensity_IntegratedIntensityEdge_Green))

merged_intens <- left_join(mean_intens, edge_intens)

# ---- Save new file ----
objectName <- str_sub(basename(objectFile), 1, -5) # name of the file without higher levels or extension
parentDir <- dirname(objectFile) # parent of the logfile
outputFile = paste(objectName, "_summary.csv") # spaces will be inserted
write_csv(merged_intens,file.path(parentDir, outputFile))

