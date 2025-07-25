import os
from pathlib import Path
import numpy as np

def eval_is_matrix(hwid: str):
    """Returns whether the given hardware ID belongs to an LED input module"""
    return "32AC:0020" in hwid

MAIN_DIR = str(Path(__file__).parent.resolve())

def get_file_path(filename: str):
    """Return the absolute path to a given file"""
    return os.path.join(MAIN_DIR, filename)

def impose(base: np.matrix, imposed: np.matrix, position: list[int]) -> np.matrix:
    """Places one Numpy matrix on top of another, clipping the boundaries"""
    top_left_bound_abs = (
        max(position[1], 0),
        max(position[0], 0)
    )
    bottom_right_bound_abs = (
        min(position[1] + imposed.shape[0], base.shape[0]),
        min(position[0] + imposed.shape[1], base.shape[1])
    )
    top_left_bound_rel = (
        max(top_left_bound_abs[0] - position[1], 0),
        max(top_left_bound_abs[1] - position[0], 0),
    )
    bottom_right_bound_rel = (
        min(bottom_right_bound_abs[0] - position[1], base.shape[0]),
        min(bottom_right_bound_abs[1] - position[0], base.shape[1])
    )

    if (
        bottom_right_bound_abs[0] < 0 or
        bottom_right_bound_abs[1] < 0 or
        top_left_bound_abs[0] > base.shape[0] or
        top_left_bound_abs[1] > base.shape[1]
    ):
        print("Out of frame")
        return base
    base[top_left_bound_abs[0]:bottom_right_bound_abs[0], top_left_bound_abs[1]:bottom_right_bound_abs[1]] = imposed[top_left_bound_rel[0]:bottom_right_bound_rel[0], top_left_bound_rel[1]:bottom_right_bound_rel[1]]
    return base