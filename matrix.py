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
        top_left_bound_abs = (
            max(position[1], 0),
            max(position[0], 0)
        )
        bottom_right_bound_abs = (
            min(position[1] + matrix.shape[0], self.matrix.shape[0]),
            min(position[0] + matrix.shape[1], self.matrix.shape[1])
        )
        top_left_bound_rel = (
            max(top_left_bound_abs[0] - position[1], 0),
            max(top_left_bound_abs[1] - position[0], 0),
        )
        bottom_right_bound_rel = (
            min(bottom_right_bound_abs[0] - position[1], self.matrix.shape[0]),
            min(bottom_right_bound_abs[1] - position[0], self.matrix.shape[1])
        )

        if (
            bottom_right_bound_abs[0] < 0 or
            bottom_right_bound_abs[1] < 0 or
            top_left_bound_abs[0] > self.matrix.shape[0] or
            top_left_bound_abs[1] > self.matrix.shape[1]
        ):
            print("Out of frame")
            return
        self.matrix[top_left_bound_abs[0]:bottom_right_bound_abs[0], top_left_bound_abs[1]:bottom_right_bound_abs[1]] = matrix[top_left_bound_rel[0]:bottom_right_bound_rel[0], top_left_bound_rel[1]:bottom_right_bound_rel[1]]

if __name__ == "__main__":
    matrix = Matrix(255)
    matrix.log_state()