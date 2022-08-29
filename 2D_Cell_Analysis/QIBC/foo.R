require(ggplot2)
require(here)
require(dplyr)
require(RColorBrewer)

mybreaks <- c(0,3,6,Inf) # bins
mylabels <- c("≤ 3", "3 - 6", "> 6","") # null added at end to avoid warning about labels and breaks being same length

# Fig 9 -----------
# colors from specified gradient end/middle points
#iris_identity <- ggplot(iris) + 
#  geom_point(aes(x=Sepal.Width, y=Sepal.Length,
#                  colour=cut(Petal.Length, mybreaks))) +
#   scale_color_identity("Petal.Length", labels=mylabels, 
#                        breaks=mybreaks, guide="legend") +
#   labs(title = "Fig. 9: Colors created to span a set of specified colors")
# 
# print(iris_identity)


# Fig 10 ---------
# based on answers from stackoverflow, adapting to scatter data
p2<- ggplot(iris, aes(x=Sepal.Width,y=Sepal.Length,fill=cut(Petal.Length, c(0,3,6,Inf)))) +
  geom_tile() +
  scale_fill_brewer(type="seq",palette = "YlGn") + # colors based on a yellow-green palette
  guides(fill=guide_legend(title="Petal Length")) +
  labs(title = "Fig. 10: Discrete color series created from the Yellow-Green palette")

print(p2)

p3 <- ggplot(iris) +
  geom_point(aes(x=Sepal.Width, y=Sepal.Length,
                 colour=cut(Petal.Length, mybreaks))) +
  theme_classic() +
  scale_colour_brewer("Petal Length", type="seq",palette = "YlGn", labels = mylabels, guide = "legend") +
  labs(title = "Fig. 11: Scatterplot with color change at specified breaks in data")

print(p3)

# This somehow produces the legend that the graphing practice script fails to do. but only after running it a few times and adding more stuff on top. 
# Did I have to get the error "Error in grDevices::col2rgb(colour, TRUE) : invalid color name '(0,3]'" ?


