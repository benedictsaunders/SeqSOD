from contextlib import contextmanager
import subprocess as sp
from glob import glob
from tqdm import tqdm
from pathlib import Path
import os

#### Handling optional packages - will only use them if the are installed
#

import importlib
pyfiglet_loader = importlib.util.find_spec('pyfiglet')
if pyfiglet_loader is not None:
    from pyfiglet import Figlet

#
####


@contextmanager
def cd(path):
    prev = os.getcwd()
    if not os.path.exists(f"{prev}/{path}"):
        os.makedirs(str(path))
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(prev)

def move_and_rename(query, prefix, directory = "ALL_STRUCTS", pbar_desc = ""):

    globbed = list(glob(query))
    for f in tqdm(globbed, desc=pbar_desc):
        name = f.split("/")[-1]
        loc = f.split("/")[:-1]
        loc = "/".join(loc)
        new = "../../" + directory + "/" + prefix + name
        p = sp.Popen(["cp", f, new])
        p.wait()

def handle_overwrite(force):
    def remove_prev():
        globbed = glob("sqsd_*")
        p = sp.Popen(["rm", "-r"] + globbed + ["ALL_STRUCTS", "endpoints"])
        p.wait()

    paths = (Path("ALL_STRUCTS"), Path("sqsd_1"))
    if force:
        if any((p.exists() for p in paths)):
            remove_prev()

    else:
        raise FileExistsError("Previous run found. Consider reviewing the parent directory, or using the enabling the overwrite option.")
    

def handle_input(supercell_str):

    #### DOESN'T ALWAYS APPEAR TO BE THE CASE ####
    #

    # supercell = [int(i) for i in supercell_str]
    # if supercell == [1,1,1]:
    #     raise ValueError("SOD cannot work with a 1x1x1 cell. Please use a primitive input and define a supercell.")

    #
    ####
    for elem in supercell_str:
        if elem == "0" or "." in elem or int(elem) < 1:
            raise ValueError("Please use positive, non-zero integers as the definition for the supercell")
        
    return 0
    
def cli_header():
    print()
    if pyfiglet_loader is not None:
        f = Figlet(font='doom')
        print(f.renderText('SeqSOD'))
    else:
        print(">>> ====== <<<")
        print(">>> SeqSOD <<<")
        print(">>> ====== <<<\n")
    print("  A sequential approach to using SOD")

