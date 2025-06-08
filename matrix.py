from const import WIDTH, HEIGHT

class Matrix:

    matrix = [[]]

    def __init__(self, color=0):
        self.fill(color)

    def fill(self, color):
        self.matrix = [[color] * WIDTH for _ in range(0, HEIGHT)]
        
    def log_state(self):
        print(self.matrix)
        for row in self.matrix:
            for col in row:
                print("#" if col > 100 else " ", end=" ")
            print()

    def set_led(self, x, y, value):
        try:
            self.matrix[y][x] = value
        except IndexError: pass

    def get_led(self, x, y):
        return self.matrix[y][x]
    
    def get_column_values(self, column):
        values = []
        for row in self.matrix:
            values.append(row[column])
        return values

if __name__ == "__main__":
    matrix = Matrix(255)
    matrix.log_state()