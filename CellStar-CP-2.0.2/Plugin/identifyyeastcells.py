#!/usr/bin/env python
import threading

from cellprofiler_core.constants.measurement import COLTYPE_FLOAT
from cellprofiler_core.constants.module import TECH_NOTE_ICON, PROTIP_RECOMMEND_ICON, PROTIP_AVOID_ICON


__doc__ = """
IdentifyYeastCells
==================

**IdentifyYeastCells** identifies yeast (or other round) objects in the image. This module was designed 
to work on brightfield images. However in some cases it can also be efficient with fluorescent imagery.

The important part of the module is parameter fitting mechanism which allows to adapt it to many different types of imagery. 

There is a number of various usage example available on website `CellStar algorithm <http://www.cellstar-algorithm.org/>`__ which includes ready to use pipelines.


What do I need as input?
^^^^^^^^^^^^^^^^^^^^^^^^
To use this module, you will need to make sure that your input image has the following qualities:

-  The image should be grayscale.

What do the settings mean?
^^^^^^^^^^^^^^^^^^^^^^^^^^
See below for help on the individual settings. The following icons are used to call attention to key items: 

-  |imageRec| Our recommendation or example use case for which a particular setting is best used.
-  |imageAvo| Indicates a condition under which a particular setting may not work well.
-  |imageTech| Technical note. Provides more detailed information on the setting.

What do I get as output?
^^^^^^^^^^^^^^^^^^^^^^^^
A set of primary objects are produced by this module, which can be used in downstream modules for measurement purposes or other operations. 

See the section *Available_measurements* below for the measurements that are produced by this module.

Once the module has finished processing, the module display window 
will show the following panels:

- *Left:* The raw, original image.
- *Right:* The identified objects shown as a color image where connected pixels that belong to the same object are assigned the same color (*label image*). It is important to note that assigned colors are arbitrary; they are used simply to help you distingush the various objects.

Available measurements
^^^^^^^^^^^^^^^^^^^^^^
**Image measurements:**

- *Count:* The number of primary objects identified.

**Object measurements:**

- *Location_X, Location_Y:* The pixel (X,Y) coordinates of the primary object centroids. The centroid is calculated as the center of mass of the binary representation of the object.
- *Features_Quality:* The module internal quality measure describing how well objects fits the model. It can be used to filter out the weakest objects.

Publications
^^^^^^^^^^^^

This module was prepared by Filip Mroz, Adam Kaczmarek and Szymon Stoma. The method uses CellStar approach 
developed by Versari et al. It is also available with a dedicated GUI for semi-automatic segmentation.

"Long-term Tracking of Budding Yeast Cells in Brightfield Microscopy: CellStar and the Evaluation Platform." 
Journal of The Royal Society Interface 14.127 (2017)

Please reach us at `CellStar algorithm <http://www.cellstar-algorithm.org/>`__ website for inquires and manuals.

Credits
^^^^^^^
Filip Mroz, Adam Kaczmarek, Szymon Stoma,
Artemis Llamosi,
Kirill Batmanov,
Cristian Versari,
Cedric Lhoussaine,
Gabor Csucs,
Simon F. Noerrelykke,
Gregory Batt,
Pawel Rychlikowski,
Pascal Hersen.

.. |imageRec| image:: {PROTIP_RECOMMEND_ICON}
.. |imageAvo| image:: {PROTIP_AVOID_ICON}
.. |imageTech| image:: {TECH_NOTE_ICON}
""".format(PROTIP_RECOMMEND_ICON=PROTIP_RECOMMEND_ICON, PROTIP_AVOID_ICON=PROTIP_AVOID_ICON,
           TECH_NOTE_ICON=TECH_NOTE_ICON)

# Module documentation variables:
__authors__ = """Filip Mroz,
Adam Kaczmarek,
Szymon Stoma    
"""
__contact__ = "fafafft@gmail.com"
__date__ = "2023.01.07"
__version__ = "2.0.2"
__docformat__ = "restructuredtext en"
__revision__ = "$Id$"

#################################
#
# Imports from useful Python libraries
#
#################################
from os.path import join as pj
from os.path import isfile
import logging

from cellprofiler_core.module.image_segmentation import ImageSegmentation
from cellprofiler_core.object import Objects
from cellprofiler_core.setting.choice import Choice
from cellprofiler_core.setting.do_something import DoSomething
from cellprofiler_core.setting.subscriber import ImageSubscriber
from cellprofiler_core.setting.text import Float, Integer, Text

logger = logging.getLogger(__name__)

import math
import numpy as np
import scipy.ndimage

#################################
#
# Imports from CellProfiler
#
##################################

import bioformats

import cellprofiler.modules
import cellprofiler_core.measurement as cpmeas
import cellprofiler_core.setting as cps
import cellprofiler_core.preferences as pref

#################################
#
# Specific imports
#
##################################

from cellstar.utils.params_util import default_parameters, create_size_weights
from cellstar.segmentation import Segmentation
from cellstar.parameter_fitting.pf_runner import run_pf, run_rank_pf
from cellstar.utils.debug_util import memory_profile, explorer_expected

###################################
#
# Constants
#
###################################

DEBUG = 1
F_BACKGROUND = "Background"
BKG_CURRENT = 'Actual image'
BKG_FIRST = 'First image'
BKG_FILE = 'File'

C_OBJECT_FEATURES = "Features"

FTR_OBJECT_QUALITY = "Quality"
'''The object quality - floating number the higher the better'''
M_OBJECT_FEATURES_OBJECT_QUALITY = '%s_%s' % (C_OBJECT_FEATURES, FTR_OBJECT_QUALITY)


def hack_add_from_file_into_EditObjects(dialog_box):
    import wx
    def on_load(event):
        with wx.FileDialog(None,
                           message="Select image with labels",
                           wildcard="Image file (*.tif,*.tiff,*.jpg,*.jpeg,*.png,*.gif,*.bmp)|*.tif;*.tiff;*.jpg;*.jpeg;*.png;*.gif;*.bmp|*.* (all files)|*.*",
                           style=wx.FD_OPEN) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            path = dlg.Path

        labels_loaded = (bioformats.load_image(path) * 255).astype(int)
        if labels_loaded.ndim == 3:
            labels_loaded = np.sum(labels_loaded, 2) / labels_loaded.shape[2]

        for l in np.unique(labels_loaded):
            if l != 0:
                dialog_box.add_label(l == labels_loaded)
        # no shape check, no float check
        dialog_box.init_labels()
        dialog_box.display()
        dialog_box.record_undo()

    ID_ACTION_LOAD_FROM_FILE = wx.NewId()
    sizer = dialog_box.toolbar.ContainingSizer
    load_file_button = wx.Button(dialog_box, ID_ACTION_LOAD_FROM_FILE, "Add from file")
    list(sizer.Children)[-1].Sizer.Add(load_file_button, 0, wx.ALIGN_CENTER)
    dialog_box.Bind(wx.EVT_BUTTON, on_load, load_file_button)


###################################
#
# The module class
#
###################################


class IdentifyYeastCells(ImageSegmentation):
    module_name = "IdentifyYeastCells"
    category = "Yeast Toolbox"
    variable_revision_number = 9
    current_workspace = ''
    fitting_image_set = None
    param_fit_progress = 0
    param_fit_progress_partial = 0

    def create_settings(self):
        super(IdentifyYeastCells, self).create_settings()

        self.input_image_name = self.x_name
        self.input_image_name.doc = "How do you call the images you want to use to identify objects?"

        self.object_name = self.y_name
        self.object_name.doc = "How do you want to call the objects identified by this module?"

        self.background_image_name = ImageSubscriber(
            "Select the empty field image", doc="""*(Used only when you select "loaded from file" background calculation strategy)*
            
            How do you call the image you want to use as background 
            image (same image will be used for every image in the workflow)?
            """)

        self.ignore_mask_image_name = ImageSubscriber(
            "Select ignore mask image", doc="""
            You can provide a ignore mark with regions in the image which are to be ignored by the algorithm in segmentation.
            """, can_be_blank=True)

        self.background_elimination_strategy = Choice(
            'Select the background calculation mode',
            [BKG_CURRENT, BKG_FILE], doc="""
            You can choose from the following options:
            
            - *loaded from file*: Use this option if your background does not change at all for all images in the series. 
            - *computed from actual image*: This is default option. The algorithm will try to automatically compute the background for each individual image. In some specific cases it is better to use manually precomputed background loaded from file.""")

        self.average_cell_diameter = Float(
            "Average cell diameter in pixels",
            30.0, minval=10, doc='''\
            The average cell diameter is used to scale many algorithm parameters. 
            Please use e.g. ImageJ to measure the average cell size in pixels.
            '''
        )

        self.advanced_cell_filtering = cps.Binary(
            'Do you want to filter cells by area?', False, doc="""
            This parameter is used for cell filtering. The algorithm creates many more cell candidates than finally accepted cells (these
            cells overlap with each other). At the final phase of algorithm the cells are selected from the ensemble of cell candidates based on the 
            "quality" measure. 
            
            Use this option if you want to absolutely prohibit too small (or too big) cells to be chosen (regardless of "quality"). 
            """)

        self.min_cell_area = Integer(
            "Minimal area of accepted cell in pixels",
            900, minval=10, doc='''*(Used only when you want to filter cells based on area)*
            
            The minimum cell area is used while final filtering of cells. 
            Please use e.g. ImageJ to measure the average cell size in pixels.
            '''
        )

        self.max_cell_area = Integer(
            "Maximum area of accepted cell in pixels",
            5 * 900, minval=10, doc='''*(Used only when you want to filter cells based on area)*
            
            The maximum cell area is used while final filtering of cells. 
            Please use e.g. ImageJ to measure the average cell size in pixels.
            '''
        )

        self.background_brighter_then_cell_inside = cps.Binary(
            'Is the area without cells (background) brighter then cell interiors?', True, doc="""
            Please check if the area inside of the cells is **darker** than the area without the cells (background). Use e.g. ImageJ to measure 
            average intensity.
            """
        )

        self.bright_field_image = cps.Binary(
            'Do you want to segment brightfield images?', True, doc="""
            Choose this option if you want to segment a brightfield image. For segmentation of fluorescent images please answer "No". 
            """
        )

        self.advanced_parameters = cps.Binary(
            'Use advanced configuration parameters?', False, doc="""
            Do you want to use advanced parameters to configure plugin? They allow for more flexibility, and require 
            understanding of the algorithm to configure well.
            """
        )

        self.segmentation_precision = Integer(
            "Segmentation precision",
            2, minval=1, maxval=5, doc='''*(Used only when you want to specify advanced parameters)*
            
            Describes how thoroughly the algorithm searches for cells. Higher values should 
            make it easier to find smaller cells because the more parameters sets are searched. 
            The cost is longer runtime.
            
            |imageRec| Recommendations: 
            Start with relatively high value (e.g. 4).
            
            If you are satisfied with results, lower the value by 1 until discovered objects still look OK 
                
            .. |imageRec| image:: {PROTIP_RECOMMEND_ICON}
            '''.format(PROTIP_RECOMMEND_ICON=PROTIP_RECOMMEND_ICON)
        )

        self.specify_precision_details = cps.Binary(
            "Do you want to edit details of segmentation precision?", False,
            doc='''*(Used only when you want to specify advanced parameters)*
            
            Do you want to edit details of segmentation precision?
            
            |imageTech| These are low level parameters that can be modified
            to further tweak result.
            
            .. |imageTech| image:: {TECH_NOTE_ICON}
            '''.format(TECH_NOTE_ICON=TECH_NOTE_ICON))

        self.iterations = Integer(
            "Iterations",
            6, minval=1, maxval=15, doc='''*(Used only when you want to specify precision details)*
            
            Number of segmentation iterations done by CellStar.''')

        self.seeds_border = Float(
            "Seeds from border",
            1.2, minval=0, maxval=5, doc='''*(Used only when you want to specify precision details)*
            
            How many seeds are to be extracted from this source:
            
            - val = 0 - no seeds from this source
            - val in (0.0, 0.5] - seeds only from second iteration
            - val in (0.5, 1) - seeds only in first iteration
            - val = 1 - seeds in every iteration
            - val in (1, 5.0) - additional random seeding: val*seeds_num total
            ''')

        self.seeds_content = Float(
            "Seeds from content",
            1.2, minval=0, maxval=5, doc=self.seeds_border.doc)

        self.seeds_centroid = Float(
            "Seeds from centroid",
            1.2, minval=0, maxval=5, doc=self.seeds_border.doc)

        self.contour_points = Integer(
            "Contour points",
            44, minval=36, maxval=70, doc='''*(Used only when you want to specify precision details)*
            
            Number of points in every contour.''')

        self.contour_precision = Float(
            "Contour precision",
            49.75, minval=25, maxval=200, doc='''*(Used only when you want to specify precision details)*
            
            Number of space points covering average cell diameter.''')

        self.weights_number = Integer(
            "Cell size variants",
            2, minval=1, maxval=4, doc='''*(Used only when you want to specify precision details)*
            
            Number of tested difference size weights in every cell grow.''')

        self.maximal_cell_overlap = Float(
            "Maximal overlap allowed while final filtering of cells",
            0.2, minval=0, maxval=1, doc='''*(Used only when you want to specify advanced parameters)*
            
            This parameter is used for cell filtering. The algorithm creates many more cell candidates than finally accepted cells (these
            cells overlap with each other). At the final phase of algorithm the cells are selected from the ensamble of cell candidates based on the 
            "quality" measure. One of the conditions checked while filtering is the overlap of the current candidate cell with already chosen cells. 
            Use this parameter if you want to allow to choose cells even if they overlap. Important: at the end cells do not overlap - they are 
            trimmed in such a way that the cell of higher "quality" will "borrow" the area of lower "quality" cells. 
            '''
        )

        self.autoadaptation_steps = Integer(
            "Number of steps in the autoadaptation procedure",
            1, minval=1, maxval=1000, doc='''
            Describes how thoroughly we want to adapt the algorithm to current image sets. Higher values should 
            make it easier to correctly discover cells, however you will have to wait longer for the autoadaptation
            procedure to finish. Remember that you do it once for all images, and you can copy the values from other
            pipelines, if you have already found the parameters before. 
            '''
        )

        self.use_ground_truth_to_set_params = DoSomething("", "Autoadapt parameters",
                                                              self.ground_truth_editor, doc="""
            Use this option to autoadapt parameters required for correct contour identification. This procedure should be run once
            for one image in the series. Using your input the algorithm "learns" to recognize cells. When you click this button the window will open.
            Please select one of the images which you would like to segment. If you use background or ignore mask images you will have to provide them as well.
            On the input image you should draw few cells (3-6) and click "Done". Then the
            "learning" procedure will start. Please be patient. Usually single iteration lasts 1-3 min. The more iterations you will choose, the more likely
            it is that the algorithm will work better on your images.
            
            
            There is an experimental alternative to selecting existing image files which may be useful when images are "produced" by the pipeline:
            
            1. Start Test Run and step down to IdentifyYeastCells module
            2. Step through IdentifyYeastCells - it will run segmentation and remember input images.
            3. Now you can adapt without specifing any images.
            
            
            |imageRec| Recommendations:        
            - Start with single iteration, then check how well the algorithm is able to recognize your cells.
            - If you have more time, use more iterations. You can always cancel (it will last 1-5 min). The algorithm will then remember the best parameters learned during the session.
            - Parameters are stored as a text in "Autoadapted parameters". If you found good parameters for your datasets you can copy them to another pipeline.
            
            .. |imageRec| image:: {PROTIP_RECOMMEND_ICON}
            """.format(PROTIP_RECOMMEND_ICON=PROTIP_RECOMMEND_ICON))

        self.show_autoadapted_params = cps.Binary(
            'Do you want to see autoadapted parameters?', False, doc="""*(Used only when you want to specify advanced parameters)*
            
            Use this option to display autoadapted parameters.""")

        self.autoadapted_params = Text(text="Autoadapted parameters: ",
                                           value="[[0.0442, 304.45, 15.482, 189.40820000000002], [300, 10, 0, 18, 10]]",
                                           doc="""*(Used only when you want to specify advanced and autoadapted parameters)*
            
            Autoadapted parameters are pasted here from the "learning" preocedure. These parameters are used to characterize cell borders. 
            Edit them only if you know what you are doing. If you found good parameters for your datasets
            you can copy them to another pipeline.
            """)

    PRECISION_PARAMS_START = 18
    PRECISION_PARAMS_END = 24

    def settings(self):
        return [self.input_image_name,
                self.object_name,
                self.average_cell_diameter,
                self.segmentation_precision,
                self.maximal_cell_overlap,
                self.background_image_name,
                self.advanced_parameters,
                self.background_brighter_then_cell_inside,
                self.bright_field_image,
                self.min_cell_area,
                self.max_cell_area,
                self.advanced_cell_filtering,
                self.background_elimination_strategy,
                self.show_autoadapted_params,
                self.autoadapted_params,
                self.autoadaptation_steps,
                self.ignore_mask_image_name,
                self.specify_precision_details,
                self.iterations,
                self.seeds_border,
                self.seeds_content,
                self.seeds_centroid,
                self.contour_points,
                self.contour_precision,
                self.weights_number,
                ]

    def visible_settings(self):
        visible_settings = [self.input_image_name,
                            self.object_name,
                            self.average_cell_diameter,
                            ]

        visible_settings += [self.bright_field_image,
                             self.background_brighter_then_cell_inside,
                             self.autoadaptation_steps,
                             self.use_ground_truth_to_set_params,
                             self.show_autoadapted_params]

        if self.show_autoadapted_params:
            visible_settings.append(self.autoadapted_params)

        visible_settings.append(self.advanced_parameters)

        #
        # Show the user the background only if self.provide_background is checked
        #
        if self.advanced_parameters:
            visible_settings.append(self.segmentation_precision)

            visible_settings.append(self.specify_precision_details)
            if self.specify_precision_details:
                visible_settings.append(self.iterations)
                visible_settings.append(self.seeds_border)
                visible_settings.append(self.seeds_content)
                visible_settings.append(self.seeds_centroid)
                visible_settings.append(self.contour_points)
                visible_settings.append(self.contour_precision)
                visible_settings.append(self.weights_number)

            visible_settings.append(self.maximal_cell_overlap)
            visible_settings.append(self.advanced_cell_filtering)
            if self.advanced_cell_filtering:
                visible_settings.append(self.min_cell_area)
                visible_settings.append(self.max_cell_area)
            # Show the user the background only if self.provide_background is checked
            visible_settings.append(self.background_elimination_strategy)  #

            if self.background_elimination_strategy == BKG_FILE:
                visible_settings.append(self.background_image_name)

            visible_settings.append(self.ignore_mask_image_name)

        return visible_settings

    def on_setting_changed(self, setting, pipeline):
        '''If precision is changed then update all the related settings'''
        if setting == self.segmentation_precision or \
                                setting == self.specify_precision_details and not self.specify_precision_details.value:
            self.set_ui_from_precision(self.segmentation_precision.value)

    def is_interactive(self):
        return False

    def prepare_group(self, workspace, grouping, image_numbers):
        '''Erase module information at the start of a run'''
        d = self.get_dictionary(workspace.image_set_list)
        d.clear()
        return True

    def get_ws_dictionary(self, workspace):
        return self.get_dictionary(workspace.image_set_list)

    def __get(self, field, workspace, default):
        if field in self.get_ws_dictionary(workspace):
            return self.get_ws_dictionary(workspace)[field]
        return default

    def __set(self, field, workspace, value):
        self.get_ws_dictionary(workspace)[field] = value

    def upgrade_settings(self, setting_values, variable_revision_number, module_name, from_matlab=None):
        '''Adjust setting values if they came from a previous revision

        setting_values - a sequence of strings representing the settings
                         for the module as stored in the pipeline
        variable_revision_number - the variable revision number of the
                         module at the time the pipeline was saved. Use this
                         to determine how the incoming setting values map
                         to those of the current module version.
        module_name - the name of the module that did the saving. This can be
                      used to import the settings from another module if
                      that module was merged into the current module
        from_matlab - True if the settings came from a Matlab pipeline, False
                      if the settings are from a CellProfiler 2.0 pipeline.

        Overriding modules should return a tuple of setting_values,
        variable_revision_number and True if upgraded to CP 2.0, otherwise
        they should leave things as-is so that the caller can report
        an error.
        '''
        if variable_revision_number == 2:
            setting_values = setting_values + [False]
            variable_revision_number = 3
        if variable_revision_number == 3:
            setting_values = setting_values + [True]
            variable_revision_number = 4

        if variable_revision_number < 7:
            setting_values = setting_values + ['Leave blank']  # ignore mask
            # decode precision index 3
            setting_values[3] = str(self.precision_to_ui_map[int(setting_values[3])])
            variable_revision_number = 7
        if variable_revision_number == 7:
            # fill new ones based on precision
            setting_values = setting_values + [False]
            params_from_precision = self.get_ui_params_from_precision(int(setting_values[3]))
            setting_values[20:26 + 1] = params_from_precision
            variable_revision_number = 8
        if variable_revision_number == 8:
            # two settings were removed
            setting_values = setting_values[:6] + setting_values[8:]
            variable_revision_number = 9
        if from_matlab is None:
            return setting_values, variable_revision_number
        return setting_values, variable_revision_number, from_matlab

    def display(self, workspace, figure=None):
        if self.show_window:
            figure.set_subplots((2, 1))

            title = "Input image, cycle #%d" % (workspace.measurements.image_number,)
            image = workspace.display_data.input_pixels
            labeled_image = workspace.display_data.segmentation_pixels

            ax = figure.subplot_imshow_grayscale(0, 0, image, title)
            figure.subplot_imshow_labels(1, 0, labeled_image,
                                         self.object_name.value,
                                         sharexy=ax)

    #
    # Measuremets:
    # - objects count
    # - objects location

    def get_measurement_columns(self, pipeline):
        '''Column definitions for measurements made by IdentifyPrimAutomatic'''
        columns = super(IdentifyYeastCells, self).get_measurement_columns(pipeline)
        columns += [(self.object_name.value, M_OBJECT_FEATURES_OBJECT_QUALITY, COLTYPE_FLOAT)]

        return columns

    def get_categories(self, pipeline, object_name):
        """Return the categories of measurements that this module produces

        object_name - return measurements made on this object (or 'Image' for image measurements)
        """
        result = super(IdentifyYeastCells, self).get_categories(pipeline, object_name)
        result += [C_OBJECT_FEATURES]
        return result

    def get_measurements(self, pipeline, object_name, category):
        """Return the measurements that this module produces
        
        object_name - return measurements made on this object (or 'Image' for image measurements)
        category - return measurements made in this category
        """
        result = super(IdentifyYeastCells, self).get_measurements(pipeline, object_name, category)
        if category == C_OBJECT_FEATURES:
            result += [FTR_OBJECT_QUALITY]
        return result

    ui_to_precision_map = dict([(1, 9), (2, 11), (3, 12), (4, 13), (5, 15)])
    precision_to_ui_map = dict([(v, k) for k, v in ui_to_precision_map.items()] + [(10, 2)])

    @property
    def decoded_segmentation_precision_value(self):
        return self.ui_to_precision_map[self.segmentation_precision.value]

    @memory_profile
    def run(self, workspace):
        input_image_name = self.input_image_name.value
        self.current_workspace = workspace
        image_set = workspace.image_set

        # same image_set for fitting
        self.fitting_image_set = image_set

        #
        # Load images from workspace
        #
        input_pixels, background_pixels, ignore_mask_pixels = self.get_input_images_from_image_set(image_set)

        input_image = image_set.get_image(input_image_name, must_be_grayscale=True)
        self.input_image_file_name = input_image.file_name
        self.current_workspace.display_data.input_pixels = input_pixels

        #
        # Preprocessing
        #
        input_pixels, background_pixels, ignore_mask_pixels = self.preprocess_images(input_pixels, background_pixels,
                                                                                     ignore_mask_pixels)

        #
        # Segmentation
        #
        objects, objects_qualities, background_pixels = self.segmentation(input_pixels, background_pixels,
                                                                          ignore_mask_pixels)
        objects.parent_image = input_image

        if self.__get(F_BACKGROUND, workspace, None) is None and self.background_elimination_strategy == BKG_FIRST:
            self.__set(F_BACKGROUND, workspace, background_pixels)

        workspace.object_set.add_objects(objects, self.object_name.value)

        # Save measurements
        workspace.measurements.add_measurement(self.object_name.value, M_OBJECT_FEATURES_OBJECT_QUALITY,
                                               objects_qualities)
        super(IdentifyYeastCells, self).add_measurements(workspace)

    def set_params_from_ui(self, params):
        def update_params(next_name, first_name, random_name, ui_value):
            params["segmentation"]["seeding"]["from"][next_name] = ui_value >= 1 or ui_value <= 0.5
            params["segmentation"]["seeding"]["from"][first_name] = ui_value > 0.5
            params["segmentation"]["seeding"]["from"][random_name] = max(0, ui_value - 1)

        params_seeding = params["segmentation"]["seeding"]["from"]
        params["segmentation"]["steps"] = self.iterations.value
        update_params("cellBorderRemovingCurrSegments", "cellBorder", "cellBorderRandom", self.seeds_border.value)
        update_params("cellContentRemovingCurrSegments", "cellContent", "cellContentRandom", self.seeds_content.value)
        params_seeding["cellBorderRemovingCurrSegmentsRandom"] = params_seeding["cellBorderRandom"]
        params_seeding["cellContentRemovingCurrSegmentsRandom"] = params_seeding["cellContentRandom"]

        params["segmentation"]["seeding"]["from"]["snakesCentroids"] = self.seeds_centroid.value > 0.0
        params["segmentation"]["seeding"]["from"]["snakesCentroidsRandom"] = max(0, self.seeds_centroid.value - 1)

        params["segmentation"]["stars"]["points"] = self.contour_points.value
        params["segmentation"]["stars"]["step"] = 1.0 / self.contour_precision.value

        default_size_weight_average = np.average(params["segmentation"]["stars"]["sizeWeight"])
        params["segmentation"]["stars"]["sizeWeight"] = list(
            create_size_weights(default_size_weight_average, self.weights_number.value)
        )

    def get_ui_params_from_precision(self, ui_precision):
        def params_to_ui(params_seeding, next_name, first_name, random_name):
            random = params_seeding[random_name]
            next = params_seeding[next_name]
            first = params_seeding[first_name]

            if random != 0:
                return random + 1
            elif next and first:
                return 1
            elif first:
                return 0.7
            elif next:
                return 0.5
            return 0.0

        def override_random_seeds_number(precision, value):
            if precision == 2:
                return max(value, 1.2)
            elif precision >= 3:
                return max(value, 1.5)
            return value

        params = default_parameters(self.ui_to_precision_map[ui_precision], 30)

        ui_params = [params["segmentation"]["steps"]]
        params_seeding = params["segmentation"]["seeding"]["from"]
        ui_params.append(override_random_seeds_number(ui_precision,
            params_to_ui(params_seeding, "cellBorderRemovingCurrSegments", "cellBorder", "cellBorderRandom")))
        ui_params.append(override_random_seeds_number(ui_precision,
            params_to_ui(params_seeding, "cellContentRemovingCurrSegments", "cellContent", "cellContentRandom")))
        ui_params.append(override_random_seeds_number(ui_precision,
            params_to_ui(params_seeding, "snakesCentroids", "snakesCentroids", "snakesCentroidsRandom")))

        ui_params.append(params["segmentation"]["stars"]["points"])
        ui_params.append(1.0 / params["segmentation"]["stars"]["step"])
        ui_params.append(len(params["segmentation"]["stars"]["sizeWeight"]))

        return ui_params

    def set_ui_from_precision(self, ui_precision):
        ui_precision_values = self.get_ui_params_from_precision(ui_precision)
        ui_precision_settings = self.settings()[self.PRECISION_PARAMS_START:self.PRECISION_PARAMS_END + 1]
        for setting, value in zip(ui_precision_settings, ui_precision_values):
            setting.value = value

    def prepare_cell_star_object(self, segmentation_precision):
        cellstar = Segmentation(segmentation_precision, self.average_cell_diameter.value)
        cellstar.parameters["segmentation"]["maxOverlap"] = self.maximal_cell_overlap.value
        self.set_params_from_ui(cellstar.parameters)

        if self.advanced_cell_filtering.value:
            def calculate_area_multiplier(area):
                return 4.0 * area / self.average_cell_diameter.value ** 2 / math.pi

            # def calculate_size_multiplier(area):
            #    return calculate_area_multiplier(area) ** 0.5

            areas_range = self.min_cell_area.value, self.max_cell_area.value
            cellstar.parameters["segmentation"]["minArea"] = max(cellstar.parameters["segmentation"]["minArea"],
                                                                 calculate_area_multiplier(areas_range[0]))
            cellstar.parameters["segmentation"]["maxArea"] = calculate_area_multiplier(areas_range[1])
            # to some extent change length of rays
            # cellstar.parameters["segmentation"]["stars"]["maxSize"] = max(cellstar.parameters["segmentation"]["stars"]["maxSize"], min(2.5, calculate_size_multiplier(areas_range[1])))

        success = cellstar.decode_auto_params(self.autoadapted_params.value)
        if not success:  # if current value is invalid overwrite it with current settings
            self.autoadapted_params.value = cellstar.encode_auto_params()
        return cellstar

    @staticmethod
    def normalized_log(image, sigma):
        '''Perform the Laplacian of Gaussian transform on the image

        image - 2-d image array
        mask  - binary mask of significant pixels
        size  - length of side of square kernel to use
        sigma - standard deviation of the Gaussian
        '''
        size = int(sigma * 4) + 1

        half_size = size / 2
        i, j = np.mgrid[-half_size:half_size + 1,
               -half_size:half_size + 1].astype(float) / float(sigma)
        distance = (i ** 2 + j ** 2) / 2
        gaussian = np.exp(-distance)
        #
        # Normalize the Gaussian
        #
        gaussian = gaussian / np.sum(gaussian)

        log = (distance - 1) * gaussian
        #
        # Normalize the kernel to have a sum of zero
        #
        log_norm = log - np.mean(log)
        output = scipy.ndimage.convolve(image, log_norm, mode='nearest')
        return output

    def preprocess_images(self, input_image, background_image, ignore_mask):
        # Invert images if required.
        if not self.background_brighter_then_cell_inside:
            input_image = 1 - input_image
            if background_image is not None:
                background_image = 1 - background_image

        # support for fluorescent images
        # here it is design question: we assume that the user *should* say
        # truth about background and inside of cells: insides are brighter
        # than background (so the bkg and image for fluorescent will be
        # inverted at this stage)
        if not self.bright_field_image:
            sigma = 4
            factor = 10
            edge_pixels = IdentifyYeastCells.normalized_log(input_image, sigma)
            input_image = np.subtract(input_image, factor * edge_pixels)

        return input_image, background_image, ignore_mask

    #
    # Segmentation of the image into yeast cells.
    # Returns: yeast cells, yeast cells qualities, background
    #
    def segmentation(self, normalized_image, background_pixels, ignore_mask_pixels=None):
        cellstar = self.prepare_cell_star_object(self.decoded_segmentation_precision_value)

        if self.input_image_file_name is not None:
            dedicated_image_folder = pj(pref.get_default_output_directory(), self.input_image_file_name)
            if dedicated_image_folder is not None:
                cellstar.debug_output_image_path = dedicated_image_folder

        cellstar.set_frame(normalized_image)
        cellstar.set_background(background_pixels)
        cellstar.set_mask(ignore_mask_pixels)
        segmented_image, snakes = cellstar.run_segmentation()

        objects = Objects()
        objects.segmented = segmented_image
        objects.unedited_segmented = segmented_image
        objects.small_removed_segmented = np.zeros(normalized_image.shape)

        self.current_workspace.display_data.segmentation_pixels = objects.segmented

        raw_qualities = [-s.rank for s in snakes]
        if not raw_qualities == []:
            raw_interval = min(raw_qualities), max(raw_qualities)
            logger.info("Qualities are in interval [%.3f,%.3f]." % raw_interval)

        return objects, np.array(raw_qualities), cellstar.images.background

    def fit_parameters(self, input_image, background_image, ignore_mask_image, ground_truth_labels, number_of_steps,
                       update_callback, wait_callback):
        """

        :param wait_callback: function that wait and potentially updates UI
        :param update_callback: function that take number of steps completed and return if fitting should be continued
        """
        keep_going = True

        self.param_fit_progress = 0
        self.best_snake_score = 10
        self.best_rank_score = 1000000000
        aft_active = []
        adaptations_stopped = False
        cellstar = self.prepare_cell_star_object(min(11, self.decoded_segmentation_precision_value))
        self.best_parameters = cellstar.parameters
        self.autoadapted_params.value = cellstar.encode_auto_params()

        try:
            while (keep_going or not adaptations_stopped) and self.param_fit_progress < number_of_steps:
                # here put one it. of fitting instead
                wait_callback(0.5)

                # Thread ended with exception so optimisation have to be stopped.
                if any(aft_active) and aft_active[0].exception is not None:
                    break

                # Clean aft_active from dead threads.
                while any(aft_active) and (not aft_active[0].is_alive() and aft_active[0].started):
                    aft_active = aft_active[1:]

                # If thread in line start first of them.
                if any(aft_active) and not aft_active[0].started:
                    # update parameters which may already be changed
                    aft_active[0].update_params(self.best_parameters)
                    aft_active[0].start()

                adaptations_stopped = aft_active == []

                if adaptations_stopped and keep_going and self.param_fit_progress < number_of_steps:
                    aft_active.append(
                        AutoFitterThread(run_pf, self.update_snake_params,
                                         input_image, background_image, ignore_mask_image, ground_truth_labels,
                                         self.best_parameters,
                                         self.decoded_segmentation_precision_value, self.average_cell_diameter.value,
                                         self.update_partial_iteration_progress))

                    aft_active.append(
                        AutoFitterThread(run_rank_pf, self.update_rank_params,
                                         input_image, background_image, ignore_mask_image, ground_truth_labels,
                                         self.best_parameters,
                                         self.update_partial_iteration_progress))

                # here update params. in the GUI
                keep_going_update = update_callback(self.param_fit_progress + self.param_fit_progress_partial)
                keep_going = keep_going and keep_going_update

        finally:
            update_callback(number_of_steps)

    def fit_parameters_with_ui(self, input_image, background_image, ignore_mask_image, ground_truth_labels):
        import wx
        # reading GT from dialog_box.labels[0] and image from self.pixel
        progress_max = self.autoadaptation_steps.value * 2  # every step consists of: snake params and ranking params fitting

        with wx.ProgressDialog("Fitting parameters..", "Iterations remaining", progress_max * 100,
                               # show percents of change
                               style=wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME) as dialog:
            def update(steps):
                return dialog.Update(steps * 100)[0]

            def wait(time):
                return wx.Sleep(int(time + 0.5))

            self.fit_parameters(input_image, background_image, ignore_mask_image, ground_truth_labels, progress_max,
                                update, wait)

    def get_param_fitting_input_images_from_image_set(self):
        """
        Try to load images from current workspace. Can be used when fitting is called in test run after segmentation has been
        run at least once.
        """
        if self.fitting_image_set is None:
            return None

        images = self.get_input_images_from_image_set(self.fitting_image_set)
        if images is None:
            return None
        return images + (None,)

    def get_input_images_from_image_set(self, image_set):
        try:
            background_needed = self.background_elimination_strategy == BKG_FILE
            ignore_mask_needed = self.ignore_mask_image_name.value != 'Leave blank'

            background_image = None
            ignore_mask = None

            # load images from workspace
            input_image = image_set.get_image(self.input_image_name.value, must_be_grayscale=True).pixel_data
            if background_needed:
                background_image = image_set.get_image(self.background_image_name.value,
                                                       must_be_grayscale=True).pixel_data
            if ignore_mask_needed:
                ignore_mask_image = image_set.get_image(self.ignore_mask_image_name.value)
                ignore_mask = ignore_mask_image.pixel_data > 0

            return input_image, background_image, ignore_mask
        except Exception as ex:
            logger.info("Could not use image from workspace.image_set because: " + str(ex))
            return None

    @staticmethod
    def load_image_grayscale(path):
        image = bioformats.load_image(path)
        if image.ndim == 3:
            image = np.sum(image, 2) / image.shape[2]
        return image

    def get_param_fitting_input_images_from_user(self):
        import wx
        def get_file_path(message):
            with wx.FileDialog(None,
                               message=message,
                               wildcard="Image file (*.tif,*.tiff,*.jpg,*.jpeg,*.png,*.gif,*.bmp)|*.tif;*.tiff;*.jpg;*.jpeg;*.png;*.gif;*.bmp|*.* (all files)|*.*",
                               style=wx.FD_OPEN) as dlg:
                if dlg.ShowModal() == wx.ID_OK:
                    return dlg.Path
                else:
                    return None

        input_image = None
        background_image = None
        ignore_mask = None
        labels = None

        background_needed = self.background_elimination_strategy == BKG_FILE
        ignore_mask_needed = self.ignore_mask_image_name.value != 'Leave blank'

        message = "In order to autoadapt parameters you need to provide:\n- input image"
        if background_needed:
            message += "\n- background image"

        if ignore_mask_needed:
            message += "\n- ignore mask image"

        with wx.MessageDialog(None, message, "Select images for autoadapt", wx.OK | wx.ICON_INFORMATION) as dlg:
            dlg.ShowModal()

        input_image_path = get_file_path("Select sample input image")
        if input_image_path is None:
            return None
        else:
            input_image = self.load_image_grayscale(input_image_path)
            label_path = input_image_path + ".lab.png"  # if file attached load labels from file
            if isfile(label_path):
                labels = (self.load_image_grayscale(label_path) * 255).astype(int)

        if background_needed:
            background_image_path = get_file_path("Select background image")
            if background_image_path is None:
                return None
            else:
                background_image = self.load_image_grayscale(background_image_path)

        if ignore_mask_needed:
            ignore_mask_path = get_file_path("Select ignore mask image")
            if ignore_mask_path is None:
                return None
            else:
                ignore_mask = self.load_image_grayscale(ignore_mask_path) > 0

        return input_image, background_image, ignore_mask, labels

    def ground_truth_editor(self):
        import wx
        from cellprofiler.gui.editobjectsdlg import EditObjectsDialog

        '''Display a UI for GT editing'''
        ### check if user want to use last pipeline run images
        pipeline_imagery = self.get_param_fitting_input_images_from_image_set()
        if pipeline_imagery is not None:
            # ask if user want to use it
            with wx.MessageDialog(None,
                                  "Images used in previous pipeline run are available. Do you want to use them for autoadapting?",
                                  "Using pipeline images", wx.YES_NO | wx.ICON_QUESTION) as dlg:
                use_pipeline = dlg.ShowModal()
            if use_pipeline == wx.ID_NO:
                pipeline_imagery = None

        ### opening file dialogs
        input_data = pipeline_imagery or self.get_param_fitting_input_images_from_user()
        if input_data is None:
            return
        input_image, background_image, ignore_mask, labels = input_data

        ### opening GT editor
        title = "Please mark few representative cells to allow for autoadapting parameters. \n"
        title += " \n"
        title += 'Press "F" to being freehand drawing.\n'
        title += "Click Help for full instructions."

        if labels is None or not labels.any():
            edit_labels = [np.zeros(input_image.shape[:2], int)]

            if getattr(self, "last_labeling", None) is not None:
                if self.last_labeling[0] == hash(abs(np.sum(input_image))):
                    edit_labels = [self.last_labeling[1]]

            ## two next lines are hack from Lee
            edit_labels[0][0, 0] = 1
            edit_labels[0][-2, -2] = 1
            with EditObjectsDialog(
                    input_image, edit_labels, False, title) as dialog_box:
                hack_add_from_file_into_EditObjects(dialog_box)
                result = dialog_box.ShowModal()
                if result != wx.OK:
                    return None
                labels = dialog_box.labels[0]
            ## two next lines are hack from Lee
            labels[0, 0] = 0
            labels[-2, -2] = 0

            self.last_labeling = (hash(abs(np.sum(input_image))), labels)

        # check if the user provided GT
        if not labels.any():
            with wx.MessageDialog(None,
                                  "Please correctly select at least one cell. Otherwise, parameters can not be autoadapted!",
                                  "Warning!", wx.OK | wx.ICON_WARNING) as dlg:
                dlg.ShowModal()
            return

        input_processed, background_processed, ignore_mask_processed = self.preprocess_images(input_image,
                                                                                              background_image,
                                                                                              ignore_mask)

        self.fit_parameters_with_ui(input_processed, background_processed, ignore_mask_processed, labels)

    def update_partial_iteration_progress(self, fraction):
        self.param_fit_progress_partial = min(0.99, max(self.param_fit_progress_partial, fraction))

    def update_snake_params(self, new_parameters, new_snake_score):
        if new_snake_score < self.best_snake_score:
            self.best_snake_score = new_snake_score
            self.best_parameters = new_parameters
            self.best_rank_score = 1000000000  # clear best ranking params as it no longer valid for different snakes
            if self.autoadapted_params.value != Segmentation.encode_auto_params_from_all_params(new_parameters):
                self.autoadapted_params.value = Segmentation.encode_auto_params_from_all_params(new_parameters)
                logger.info("New auto parameters applied.")
        else:
            logger.info(
                "New auto parameters (%f) are not better than current (%f)." % (new_snake_score, self.best_snake_score))
        self.param_fit_progress += 1
        self.param_fit_progress_partial = 0

    def update_rank_params(self, new_parameters, new_rank_score):
        if new_rank_score < self.best_rank_score:
            self.best_rank_score = new_rank_score
            self.best_parameters = new_parameters
            if self.autoadapted_params.value != Segmentation.encode_auto_params_from_all_params(new_parameters):
                self.autoadapted_params.value = Segmentation.encode_auto_params_from_all_params(new_parameters)
                logger.info("New auto ranking parameters applied.")
        else:
            logger.info("New auto ranking parameters (%f) are not better than current (%f)." % (
                new_rank_score, self.best_rank_score))
        self.param_fit_progress += 1
        self.param_fit_progress_partial = 0


class AutoFitterThread(threading.Thread):
    def __init__(self, target, callback, *args):
        super(AutoFitterThread, self).__init__()
        self._target = target
        self._args = list(args)
        self._callback = callback
        self.started = False
        self.mock_alive = False
        self.exception = None

    def update_params(self, new_params):
        self._args[4] = new_params

    def run(self):
        try:
            self.started = True
            params, score = self._target(*self._args)
            self._callback(params, score)
        except:
            self.exception = True
            raise

    def start(self):
        #  check if call on the same thread because of explorer
        if not explorer_expected():
            self.started = True
            super(AutoFitterThread, self).start()
        else:
            self.mock_alive = True
            self.run()
            self.mock_alive = False

    def is_alive(self):
        if not explorer_expected():
            return super(AutoFitterThread, self).is_alive()
        else:
            return self.mock_alive

    def kill(self):
        pass
