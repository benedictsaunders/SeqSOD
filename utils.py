from contextlib import contextmanager
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
