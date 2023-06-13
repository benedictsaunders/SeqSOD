from contextlib import contextmanager
import subprocess as sp
from glob import glob
from tqdm import tqdm
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

def prepend_filenames(query, prefix):
    new_names = []
    globbed = list(glob(query))
    for f in tqdm(globbed):
        name = f.split("/")[-1]
        loc = f.split("/")[:-1]
        new = loc + "/" + prefix + name
        p = sp.Popen(["mv", f, new])
        p.wait()

    
