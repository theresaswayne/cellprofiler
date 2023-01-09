import sys
import os
import shutil
import time
import subprocess

def relative_to_absolute(path):
    if os.path.isabs(path):
        return path
    else:
        dir_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(dir_path, path)

CELLPROFILER_PATH = r"C:\Program Files\CellProfiler\CP_4_2_4\CellProfiler.exe"
CELLPROFILER_PLUGINS_PATH = r"D:\Fafa\Drozdze\AsPlugin\Release\Final 2.0.1 for CP-4.2.4\Plugin"

done_path = relative_to_absolute("done.txt")
cell_profiler_exe = [CELLPROFILER_PATH, "--do-not-fetch", '--done-file='+done_path, "--log-level=INFO", "--plugins-directory=" + CELLPROFILER_PLUGINS_PATH, "-c", "-r"]

######## USING DEVELOPMENT CODE ########
## remember to activate CellProfiler enviroinment so there is centrosome to use
##os.system("@setlocal")
##os.system(r'set PYTHONPATH=D:\Fafa\Drozdze\centrosome')
##sys.path = sys.path + [r"D:\Fafa\Drozdze\centrosome"]
#CELLPROFILER_PATH_DEV = r"D:\Fafa\Drozdze\CellProfiler\CellProfiler.py" 
##  CELLPROFILER_OFFICIAL_PLUGINS_PATH = r"D:/Fafa/Drozdze/CellProfiler-plugins"

#cell_profiler_py = ["python", CELLPROFILER_PATH_DEV, "--do-not-fetch", "--done-file=done.txt", "--log-level=INFO", "--plugins-directory=" + CELLPROFILER_PLUGINS_PATH, "-c", "-r"] 
#cell_profiler_exe = cell_profiler_py
######## ######## ######## ########

def run_cellprofiler(input, output, pipeline):
    print("""Running CellProfiler pipeline...
    Input directory: {input}
    Output directory: {output}
    Pipeline: {pipeline}""".format(input = input, output = output, pipeline = pipeline))
    # Make relative to absolute paths:
    input = relative_to_absolute(input)
    output = relative_to_absolute(output)
    pipeline = relative_to_absolute(pipeline)
    os.chdir(os.path.dirname(CELLPROFILER_PATH))
     
    param_list = cell_profiler_exe + ["-i", input, "-o", output, "-p", pipeline]
    subprocess.call(param_list)
    print("... run completed")
    
if(len(sys.argv) == 4):
    run_cellprofiler(sys.argv[1],sys.argv[2],sys.argv[3])
    # print done--file -> if fail then scream loundly!
    done = open(done_path).readlines()[0].strip()
    if done != "Complete":
        print("!!!! ERROR !!!!")
    print(done)
else:
    print("[input] [output] [pipeline]")
    print("Received:", sys.argv[1:])