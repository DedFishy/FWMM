import numpy as np
from const import WIDTH, HEIGHT
import util

class Matrix:
    """A virtual representation of an LED matrix"""

    matrix = np.matrix([[]])

    def __init__(self, color: int=0):
        self.fill(color)

    def fill(self, color: int):
        """Fill the matrix with a specific color"""
        self.matrix = np.matrix([[color] * WIDTH for _ in range(0, HEIGHT)])
    
    def impose(self, matrix: np.matrix, position: list[int]):
        """Place an LED matrix on top of the matrix at the given position"""
        self.matrix = util.impose(self.matrix, matrix, position)