import numpy as np
from const import WIDTH, HEIGHT

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
        width = min(self.matrix.shape[0] - position[1], matrix.shape[0])
        height = min(self.matrix.shape[1] - position[0], matrix.shape[1])
        self.matrix[position[1]:position[1] + width, position[0]:position[0] + height] = matrix[:width, :height]

if __name__ == "__main__":
    matrix = Matrix(255)
    matrix.log_state()