from matrix import operations 
from visualization import coordinate_grid


#matrix_rows = int(input("How many rows does the matrix have?")) #Asks the user
matrix_rows = 2
#matrix_columns = int(input("How many colums does the matrix have?")) #Asks the user
matrix_columns = 2

matrix = [[int(input(f"Enter element [{i}][{j}]: ")) for j in range(matrix_columns)] for i in range(matrix_rows)]
matrix_2 = [[int(input(f"Enter element [{i}][{j}]: ")) for j in range(matrix_columns)] for i in range(matrix_rows)]


print(operations.matrix_sub(matrix, matrix_2))
print(operations.matrix_add(matrix, matrix_2))
operations.matrix_determinant(matrix, matrix_2)

#Display the eigenvectors of the matrices using the coordinate grid visualization
coordinate_grid.matrix_display(matrix)
coordinate_grid.matrix_display(matrix_2)
