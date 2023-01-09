CELLSTAR SEGMENTATION PLUGIN FOR CELLPROFILER
version 2.0.2

1. Description 
This package contains:
- plugin for CellProfiler which provides segmentation of round cells in brightfield (method developed for Budding Yeast) 
- wide range of usage examples

2. Requirements
- CellProfiler 4.2.4
- Tested on Windows 7, Windows 8/8.1, Windows 10 and OS X 10.10.1/10.11.2
	
3. Contents:
    Plugin:
        This contains a CellStar plugin that can be used as a module in CellProfiler.
        For more information see "4. Plugin instalation"
    Examples:
        This contains examples of usage of CellStar prepared to guide users on how to properly use CellProfiler plugin. 
        For more information see "5. Example usage"
   
4. Plugin instalation
	In order to install the plugin copy the content of directory 'Plugin' into your CellProfiler Plugins directory. The path to the directory can be found and edited in CellProfiler->File-Preferences->CellProfiler plugins directory.
	
	CellProfiler at startup tries to load all the plugins in that directory. In case of errors the information along with the cause can be found in console associated with CellProfiler. If a plugins is correctly installed it should show in the appropriate module category.
	
5. Plugin usage in CellProfiler
	The modules can be found in Yeast Toolbox category as IdentifyYeastCells.
    
6. Example usage (simple)
    In order to show how to use CellStar plugin we prepared a number of examples. This should help you to set up a proper pipeline for your data imagery, as different steps may be necessary to cope with different data sets.
    
    Examples can be found in examples folder and every case should include:
    - input imagery
    - occasionally additional imagery to help segmentation (such as background, ignore mask, etc.)
    - CellProfiler pipelines (created in version 2.2) for a given case
    - Tutorial.txt which explains what steps are necessary to properly segment these type of images.
    - occasionally _Solution folder with best trained pipelines in cases where using input imagery to train is not sufficient
    
    There are two ways of running these examples:
    - manual using CellProfiler GUI and setting up default Input and Output paths (see Tutorial.txt)
    - automatic running (no GUI) of pipeline on input images using CellProfiler batch mode (see "7. Running examples in batch mode")
    
    Currently the examples cover the following cases:
    - StrongEdgeAndDark:
        These type of images are exactly what CellStar was designed for so they can be correctly segmented using default parameters.
    - InhomogeneousBackground
        These images are similar to the previous but there is a problematic background that can interfere with segmentation.
    - StrongEdgesAndGray (parameter fitting)
        Cells in these images have interiors of similar intensity to background which make finding them more difficult. Default parameters are occasionally unsuccessful but we can use auto-adapt feature to find the better ones for this dataset.
    - DarkButOverlapping (filtering)
        These images contains yeast cells which are dark and can be segmented using default setup but with no monolayer enforcement. This result in a lot of cell overlapping in the latter stage of the experiment. In order to improve the results a number of filtering methods is applied including CellProfiler Analyst classifiers.
    - BrightButOverlapping (ignore regions)
        Images acquired as previous example but with different focus so there are bright instead of dark. The overlapping problem is the same however in this case these regions can be identified and ignore.
    - FluorescentImagery (smoothing)
        CellStar was not designed for fluorescent imagery but was quickly adapted to handle these. It is still in experimental state.
    - StrongEdgesAndWhite (parameter fitting, dark/bright)
        Imagery has similar features to StrongEdgesAndGray so the solution is auto-adaptation of the parameters as well as choosing the proper dark/bright option.
        
7. Example usage (advanced - running examples in batch mode)
	In order to run example in CellProfiler in batch mode on one of example pipeline you need to:
    a) set up the paths in batch_cellprofiler.py:
        CELLPROFILER_PATH - path to CellProfiler executable
        CELLPROFILER_PLUGINS_PATH - path to CellStar Plugin directory
    b) run one of the batch files (for example 1_StrongEdgesAndDark.bat).
    
    The script runs CellProfiler in batch mode using the chosen example pipeline and input data.
	The processing of each image should take a few minutes.
    
    Batch mode requires Python in version 2.7 and was tested on Windows but should also be possible on other OSes as it is enough to call batch_cellprofiler.py script with input, output and pipeline paths.
    
    
	
	