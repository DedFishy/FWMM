import os
from pathlib import Path
import sys


def eval_is_matrix(hwid):
    return "32AC:0020" in hwid

def get_main_directory():
    return str(Path(__file__).parent.resolve())

MAIN_DIR = get_main_directory()

def get_file_path(filename):
    return os.path.join(MAIN_DIR, filename)