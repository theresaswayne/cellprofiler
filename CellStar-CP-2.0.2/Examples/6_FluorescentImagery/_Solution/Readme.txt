These are two slightly different pipelines for fluorescent channel segmentation:
- FluorescentImagery_2_BigShapeFilter which is a pipeline from example
- FluorescentImagerySegmentation which is complementing to the above pipeline. The main difference are CellStar parameters found using parameter fitting which in some cases result in a more 'stable' results. 

SETUP STEPS:

1. Add images to analyze
2. Do some image specific parameter tuning (see below).

IMPORTANT TUNING:
- you need to set Average Cell Diameter in IdentifyYeastCells as well as the filtering limits (area of cells to consider)
- you may modify shape filtering thresholds