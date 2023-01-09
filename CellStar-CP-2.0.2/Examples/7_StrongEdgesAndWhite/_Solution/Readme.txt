These are two slightly different pipelines for segmentation of white cells depending on their appearence:
- for cells with bright edges use BrightEdgesAndWhite_2_Adapted
- for cells with dark edges use DarkEdgesAndWhite_2_Adapted

The only difference between them is state of the switch 'Is area without cells (background) brighter than cell interiors?' which can also refer to intensity of cell edges.

SETUP STEPS:

1. Add images to analyze
2. Do some image specific parameter tuning (see below).

IMPORTANT TUNING:
- you need to set Average Cell Diameter in IdentifyYeastCells
- you can also specify area filtering limits0