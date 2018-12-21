# Setup ------------

# load packages if not already loaded
require(dplyr)
require(readr)
require(ggplot2)
require(here)

# read data
all_objects <- read_csv(here("data", "2018-12-12_qibcC1DNANuclei.csv"))

# pull out data by genotype
AtrWT <- all_objects %>% filter(Metadata_basename == "Atr WT")
AtrKD <- all_objects %>% filter(Metadata_basename == "Atr KD")
AtrNull <- all_objects %>% filter(Metadata_basename == "Atr-")

# Object shape and size --------

# Area of detected objects
# TODO: convert to ggplot, make panels (same scale)
# hist(all_objects$AreaShape_Area) 
# hist(AtrWT$AreaShape_Area)
# hist(AtrKD$AreaShape_Area)
# hist(AtrNull$AreaShape_Area)

# Form factor of detected objects
# TODO: convert to ggplot, make panels, same scale
# hist(all_objects$AreaShape_FormFactor) #TODO: try ggplot
# hist(AtrWT$AreaShape_FormFactor)
# hist(AtrKD$AreaShape_FormFactor)
# hist(AtrNull$AreaShape_FormFactor)

#cat(mean(all_objects$AreaShape_FormFactor < 0.5)) # how many objects are not roundish?

# relationship between area and form factor?

area_ff_plot <- ggplot(data = all_objects, aes(x=AreaShape_Area, y=AreaShape_FormFactor)) +
  geom_point(aes(colour = "red"), size = 1, alpha = 0.1) + 
  theme_classic() + # no fill
  labs(x = "Area, pixels", y = "Form factor", title = "Object shape and size for 25,000 cells") +
  guides(fill=FALSE, color=FALSE) # hide legend
#print(area_ff_plot)

# all genotypes together

area_ff_plot_color <- ggplot(data = all_objects, aes(x=AreaShape_Area, y=AreaShape_FormFactor)) +
  geom_point(aes(colour = all_objects$Metadata_basename), size = 0.5, alpha = 0.1) + 
  theme_classic() + # no fill
  labs(x = "Area, pixels", y = "Form factor", title = "Object shape and size for 25,000 cells") +
  scale_colour_discrete(name = "Genotype",
                        labels = c("Atr knockdown", expression(Atr^{"+"}), expression(Atr^{"-"}))) + # rename legend elements
  guides(colour = guide_legend(override.aes = list(size=3, alpha = 1, shape = "square"))) # symbols are solid squares in the legend
# print(area_ff_plot_color)

# each genotype separately

area_ff_WT <- ggplot(data = AtrWT, aes(x=AreaShape_Area, y=AreaShape_FormFactor)) +
  geom_point(aes(colour = "red"), size = 1, alpha = 0.1) + 
  theme_classic() + # no fill
  labs(x = "Area, pixels", y = "Form factor", 
       title = expression(paste(Form~factor~vs.~Area~","~Atr^{textstyle("+")}))) +
  guides(fill=FALSE, color=FALSE) # hide legend
#print(area_ff_WT)

area_ff_KD <- ggplot(data = AtrKD, aes(x=AreaShape_Area, y=AreaShape_FormFactor)) +
  geom_point(aes(colour = "red"), size = 1, alpha = 0.1) + 
  theme_classic() + # no fill
  labs(x = "Area, pixels", y = "Form factor", 
       title = expression(paste(Form~factor~vs.~Area~","~Atr~knockdown))) +
  guides(fill=FALSE, color=FALSE) # hide legend
#print(area_ff_KD)

area_ff_Null <- ggplot(data = AtrNull, aes(x=AreaShape_Area, y=AreaShape_FormFactor)) +
  geom_point(aes(colour = "red"), size = 1, alpha = 0.1) + 
  theme_classic() + # no fill
  labs(x = "Area, pixels", y = "Form factor", 
       title = expression(paste(Form~factor~vs.~Area~","~Atr^{textstyle("-")}))) +
  guides(fill=FALSE, color=FALSE) # hide legend
#print(area_ff_Null)

# relationship between intensity and form factor?

ff_DNA_plot_color <- ggplot(data = all_objects, aes(x=AreaShape_FormFactor, y=Intensity_IntegratedIntensity_Channel1DNACorr)) +
  geom_point(aes(colour = all_objects$Metadata_basename), size = 0.5, alpha = 0.1) + 
  theme_classic() + # no fill
  labs(x = "Form factor", y = "Nominal DNA Content", title = "Integrated DNA Intensity vs. Form Factor") +
  scale_colour_discrete(name = "Genotype",
                        labels = c("Atr knockdown", expression(Atr^{"+"}), expression(Atr^{"-"}))) + # rename legend elements
  guides(colour = guide_legend(override.aes = list(size=3, alpha = 1, shape = "square"))) # symbols are solid squares in the legend
#print(ff_DNA_plot_color)

# DNA content --------------
# TODO: convert to ggplot, panels, same scale
# hist(all_objects$Intensity_IntegratedIntensity_Channel1DNACorr, breaks = (0:100)) #TODO: try ggplot
# hist(AtrWT$Intensity_IntegratedIntensity_Channel1DNACorr, breaks= (0:100), main = "WT DNA Content")
# hist(AtrKD$Intensity_IntegratedIntensity_Channel1DNACorr, breaks= (0:100), main = "Atr KD DNA Content")
# hist(AtrNull$Intensity_IntegratedIntensity_Channel1DNACorr, breaks= (0:100), main = "Atr- DNA Content")

# DNA/EdU -----------

# convert the Metadata_basename string to a factor so we can vary the colors
all_objects$Metadata_basename <- as.factor(all_objects$Metadata_basename)

# plot all genotypes together (kinda messy)
# NB "expression" is a way to get superscripts in the legend, title, axes

dot_plot <- ggplot(data = all_objects, aes(x=Intensity_IntegratedIntensity_Channel1DNACorr,
                                           y=Intensity_MeanIntensity_Channel2EdUCorr)) +
  scale_y_log10() + # Plot y on log10 scale  
  geom_point(aes(colour = all_objects$Metadata_basename), size = 0.5, alpha = 0.1) + 
  theme_classic() + # no fill
  labs(x = "DNA Content, au", y = "EdU intensity, au", 
       title = "EdU vs. DNA Content for 25,000 cells") +
  scale_colour_discrete(name = "Genotype", 
                        labels = c("Atr knockdown", expression(Atr^{"+"}), expression(Atr^{"-"}))) + # rename legend elements
  guides(colour = guide_legend(override.aes = list(size=3, alpha = 1, shape = "square"))) # symbols are solid squares in the legend
print(dot_plot)

# plot each genotype
# NB the expression paste construction is used to get the comma into the title

WT_EdU_plot <- ggplot(data = AtrWT, aes(x=Intensity_IntegratedIntensity_Channel1DNACorr,
                                        y=Intensity_MeanIntensity_Channel2EdUCorr)) +
  scale_y_log10() + # Plot y on log10 scale  
  geom_point(aes(colour = 73), size = 0.5, alpha = 0.1) + # nice blue color 
  theme_classic() + # no fill
  guides(fill=FALSE, color=FALSE)  + # hide legend
  labs(x = "DNA Content, AU", y = "EdU intensity, AU", 
       title = expression(paste(EdU~vs.~DNA~Content~","~Atr^{textstyle("+")})))
print(WT_EdU_plot)

AtrKD_EdU_plot <- ggplot(data = AtrKD, aes(x=Intensity_IntegratedIntensity_Channel1DNACorr,
                                           y=Intensity_MeanIntensity_Channel2EdUCorr)) +
  scale_y_log10() + # Plot y on log10 scale  
  geom_point(aes(colour = 73), size = 0.5, alpha = 0.1) + # nice blue color 
  theme_classic() + # no fill
  guides(fill=FALSE, color=FALSE)  + # hide legend
  labs(x = "DNA Content, AU", y = "EdU intensity, AU", 
       title = expression(paste(EdU~vs.~DNA~Content~","~Atr~knockdown)))
print(AtrKD_EdU_plot)

AtrNull_EdU_plot <- ggplot(data = AtrNull, aes(x=Intensity_IntegratedIntensity_Channel1DNACorr,
                                           y=Intensity_MeanIntensity_Channel2EdUCorr)) +
  scale_y_log10() + # Plot y on log10 scale  
  geom_point(aes(colour = 73), size = 0.5, alpha = 0.1) + # nice blue color 
  theme_classic() + # no fill
  guides(fill=FALSE, color=FALSE)  + # hide legend
  labs(x = "DNA Content, AU", y = "EdU intensity, AU", 
       title = expression(paste(EdU~vs.~DNA~Content~","~Atr^{textstyle("-")})))
print(AtrNull_EdU_plot)

# DNA/EdU with gH2AX in color ----------

WT_EdU_gH2AX_plot <- ggplot(data = AtrWT, aes(x=Intensity_IntegratedIntensity_Channel1DNACorr,
                                        y=Intensity_MeanIntensity_Channel2EdUCorr)) +
  scale_y_log10() + # Plot y on log10 scale  
  geom_point(aes(colour = Intensity_MeanIntensity_Channel3gH2AXCorr),
             size = 0.5) + # color based on gH2AX 
  theme_classic() + # no fill
  labs(x = "DNA Content, AU", y = "EdU intensity, AU", 
       title = expression(paste(EdU~vs.~DNA~Content~","~Atr^{textstyle("+")}))) +
  scale_colour_gradientn(colours=rainbow(6), name="gH2AX Mean Intensity")
print(WT_EdU_gH2AX_plot)

# what is the actual distribution of gH2AX intensity?

gH2AX_hist <- ggplot(data = AtrWT, aes(Intensity_MeanIntensity_Channel3gH2AXCorr))  +
  geom_histogram(bins = 100) +
  theme_bw() +
  ggtitle("WT gH2AX Mean Intensity")
print(gH2AX_hist)

# cumulative distribution function
gH2AX_ecdf <- ggplot(data = AtrWT, aes(Intensity_MeanIntensity_Channel3gH2AXCorr)) +
  stat_ecdf()
print(gH2AX_ecdf)


# mybreaks <- c(0,3,6,Inf) # bins
# mylabels <- c("≤ 3", "3 - 6", "> 6") 
mybreaks <- c(0,0.0005,0.00125,0.002,Inf) # bins
mylabels <- c("≤ 0.0005", "0.0005 - 0.00125", "0.00125 - 0.002", " > 0.002") # guessed
mypalette <- "Oranges"
xlimits <- c(0,80) # determined empirically TODO: use max(range())
ylimits <- c(0.0003,0.055) # determined empirically

WT_EdU_gH2AX_binned_plot <- ggplot(data = AtrWT, aes(x=Intensity_IntegratedIntensity_Channel1DNACorr,
                                                     y=Intensity_MeanIntensity_Channel2EdUCorr)) +
  xlim(xlimits) + 
  scale_y_log10(limits = ylimits) + # Plot y on log10 scale  
  geom_point(aes(colour = cut(Intensity_MeanIntensity_Channel3gH2AXCorr, mybreaks)),
            alpha = 0.4, size = 0.5) + # color based on gH2AX bins
            theme_grey() + # grey fill
            scale_colour_brewer(expression(paste(~gamma~H2AX~intensity)), type="seq",palette = mypalette, labels = mylabels, guide = "legend") +
            guides(colour = guide_legend(override.aes = list(size=4, alpha = 1, shape = "square"))) + # symbols are solid squares in the legend
            labs(x = "DNA Content, AU", y = "EdU intensity, AU", 
                   title = expression(paste(EdU~vs.~DNA~Content~","~Atr^{textstyle("+")})))
print(WT_EdU_gH2AX_binned_plot)

KD_EdU_gH2AX_binned_plot <- ggplot(data = AtrKD, aes(x=Intensity_IntegratedIntensity_Channel1DNACorr,
                                                     y=Intensity_MeanIntensity_Channel2EdUCorr)) +
  xlim(xlimits) + 
  scale_y_log10(limits = ylimits) + # Plot y on log10 scale  
  geom_point(aes(colour = cut(Intensity_MeanIntensity_Channel3gH2AXCorr, mybreaks)),
             alpha = 0.4, size = 0.5) + # color based on gH2AX bins
  theme_grey() + # grey fill
  scale_colour_brewer(expression(paste(~gamma~H2AX~intensity)), type="seq",palette = mypalette, labels = mylabels, guide = "legend") +
  guides(colour = guide_legend(override.aes = list(size=4, alpha = 1, shape = "square"))) + # symbols are solid squares in the legend
  labs(x = "DNA Content, AU", y = "EdU intensity, AU", 
       title = expression(paste(EdU~vs.~DNA~Content~","~Atr~knockdown)))
print(KD_EdU_gH2AX_binned_plot)


Null_EdU_gH2AX_binned_plot <- ggplot(data = AtrNull, aes(x=Intensity_IntegratedIntensity_Channel1DNACorr,
                                                     y=Intensity_MeanIntensity_Channel2EdUCorr)) +
  xlim(xlimits) + 
  scale_y_log10(limits = ylimits) + # Plot y on log10 scale  
  geom_point(aes(colour = cut(Intensity_MeanIntensity_Channel3gH2AXCorr, mybreaks)),
             alpha = 0.4, size = 0.5) + # color based on gH2AX bins
  theme_grey() + # grey fill
  scale_colour_brewer(expression(paste(~gamma~H2AX~intensity)), type="seq",palette = mypalette, labels = mylabels, guide = "legend") +
  guides(colour = guide_legend(override.aes = list(size=4, alpha = 1, shape = "square"))) + # symbols are solid squares in the legend
  labs(x = "DNA Content, AU", y = "EdU intensity, AU", 
       title = expression(paste(EdU~vs.~DNA~Content~","~Atr^{textstyle("-")})))
print(Null_EdU_gH2AX_binned_plot)


# TODO: filter by form factor and/or size -------



