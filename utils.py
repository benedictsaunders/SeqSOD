from contextlib import contextmanager
import subprocess as sp
from glob import glob
from tqdm import tqdm
from pathlib import Path
import os

@contextmanager
def cd(path):
    prev = os.getcwd()
    if not os.path.exists(f"{prev}/{path}"):
        os.mkdir(str(path))
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(prev)

def move_and_rename(query, prefix, directory = "ALL_STRUCTS"):

    globbed = list(glob(query))
    for f in tqdm(globbed):
        name = f.split("/")[-1]
        loc = f.split("/")[:-1]
        loc = "/".join(loc)
        new = "../../" + directory + "/" + prefix + name
        p = sp.Popen(["cp", f, new])
        p.wait()

def handle_overwrite(force):
    def remove_prev():
        globbed = glob("sqsd_*")
        p = sp.Popen(["rm", "-r"] + globbed + ["ALL_STRUCTS"])
        p.wait()

    paths = (Path("ALL_STRUCTS"), Path("sqsd_1"))
    if force:
        if any((p.exists() for p in paths)):
            remove_prev()

    else:
        raise FileExistsError("Previous run found. Consider reviewing the parent directory, or using the enabling the overwrite option.")
    
