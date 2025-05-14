WIDTH = 9
HEIGHT = 34

class Matrix:
    def __init__(self, color=0):
        self.matrix = [[color] * WIDTH] * HEIGHT
        
    def log_state(self):
        for row in self.matrix:
            for col in row:
                print("#" if col > 100 else " ", end=" ")
            print()

if __name__ == "__main__":
    matrix = Matrix(255)
    matrix.log_state()