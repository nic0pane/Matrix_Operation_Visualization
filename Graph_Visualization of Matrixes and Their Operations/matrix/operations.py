import numpy as np

def matrix_shape(matrix , matrix_2):
    # Return the number of rows and columns
    return len(matrix and matrix_2), len(matrix[0] and matrix_2[0]) 


def matrix_add(matrix, matrix_2):
    # Return the sum of two matrices
    sum_matrix = []
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            sum_matrix.append(matrix[i][j] + matrix_2[i][j])
    return sum_matrix


def matrix_sub(matrix, matrix_2):
    # Return the difference of two matrices
    diff_matrix = []
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            diff_matrix.append(matrix[i][j] - matrix_2[i][j])
    return diff_matrix


def matrix_multiply(matrix, matrix_2):
    # Return the product of two matrices
    multiply_matrix = []
    for i in range(len(matrix)):
        for j in range(len(matrix_2[0])):
            multiply_matrix.append(sum(matrix[i][k] * matrix_2[k][j] for k in range(len(matrix_2))))
    return multiply_matrix


def matrix_transpose(matrix, matrix_2): #The transpose of a matrix is obtained by swapping its rows and columns.
    transpose_matrix = []
    traspose_matrix_2 = []

    for i in range(len(matrix[0])):
        for j in range(len(matrix)):
            transpose_matrix.append(matrix[j][i])

    for i in range(len(matrix_2[0])):
        for j in range(len(matrix_2)):
            traspose_matrix_2.append(matrix_2[j][i])

    print(f"The transpose of the first matrix is: {transpose_matrix}")
    print(f"The transpose of the second matrix is: {traspose_matrix_2}")


def matrix_determinant(matrix, matrix_2): #To calculate the determinant of a matrix, we can use the formula for the determinant of a 2x2 matrix or use recursion for larger matrices.
    determinant_matrix = 0 #For now only 2x2 matrices are supported, so we will use the formula for the determinant of a 2x2 matrix.
    determinant_matrix_2 = 0

    if len(matrix) == 2 and len(matrix[0]) == 2:
        determinant_matrix = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

    if len(matrix_2) == 2 and len(matrix_2[0]) == 2:
        determinant_matrix_2 = matrix_2[0][0] * matrix_2[1][1] - matrix_2[0][1] * matrix_2[1][0]

    print(f"The determinant of the first matrix is: {determinant_matrix}")
    print(f"The determinant of the second matrix is: {determinant_matrix_2}")

    return determinant_matrix, determinant_matrix_2


def matrix_inverse(matrix, matrix_2): #To do the inverse of a matrix, we need to find the determinant of the matrix and then use it to find the inverse.
    inverse_matrix = []
    inverse_matrix_2 = []

    determinant_matrix = matrix_determinant(matrix, matrix_2)
    
    if determinant_matrix != 0:
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                inverse_matrix.append(matrix[j][i] / determinant_matrix)

    if determinant_matrix != 0:
        for i in range(len(matrix_2)):
            for j in range(len(matrix_2[0])):
                inverse_matrix_2.append(matrix_2[j][i] / determinant_matrix)

    print(f"The inverse of the first matrix is: {inverse_matrix}")
    print(f"The inverse of the second matrix is: {inverse_matrix_2}")

    
def matrix_display(matrix, matrix_2):
    print("Matrix 1:")
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            print(matrix[i][j], end=" ")
        print()
    print("Matrix 2:")
    for i in range(len(matrix_2)):
        for j in range(len(matrix_2[0])):
            print(matrix_2[i][j], end=" ")
        print()


def eigen_values(matrix, matrix_2):
    # To calculate the eigenvalues of a matrix, we can use the characteristic polynomial and find its roots.
    eigenvalues = np.linalg.eig(matrix)
    eigenvalues_2 = np.linalg.eig(matrix_2)

    pass


def eigen_vectors(matrix, matrix_2):
    # To calculate the eigenvectors of a matrix, we can use the eigenvalues and solve the system of equations (A - λI)v = 0, where A is the matrix, λ is the eigenvalue, I is the identity matrix, and v is the eigenvector.
    eigenvectors = np.linalg.eig(matrix)
    eigenvestors_2 = np.linalg.eig(matrix_2)
    
    pass


