import numpy as np
from const import WIDTH, HEIGHT
import util

class Matrix:

    matrix = np.matrix([[]])

    def __init__(self, color=0):
        self.fill(color)

    def fill(self, color):
        self.matrix = np.matrix([[color] * WIDTH for _ in range(0, HEIGHT)])
        
    def log_state(self):
        pass
        #for row in self.matrix:
        #    print(row)
        #    for col in row:
        #        
        #        print("#" if (col > 100) else " ", end=" ")
        #    print()

    def set_led(self, x, y, value):
        try:
            self.matrix[x,y] = value
        except IndexError: pass

    def get_led(self, x, y):
        return self.matrix[y,x]
    
    def get_column_values(self, column):
        values = []
        for row in self.matrix.tolist():
            values.append(row[column])
        return values
    
    def impose(self, matrix: np.matrix, position):
        self.matrix = util.impose(self.matrix, matrix, position)

if __name__ == "__main__":
    matrix = Matrix(255)
    matrix.log_state()