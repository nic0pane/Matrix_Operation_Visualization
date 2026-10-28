#Determinant using the original 2x2 formula / Gaussian elimination.
from .elimination import eliminate
from .operations import (CalculationResult,record_step,format_number,require_square,validate_scalar)

def matrix_determinant(matrix, verbose=False, *, record_steps=False):
    matrix_size = require_square(matrix)
    should_record_steps = record_steps or verbose

    if matrix_size <= 2:
        if matrix_size == 1:
            determinant_value = float(matrix[0][0])
        else:
            main_diagonal_product = matrix[0][0] * matrix[1][1]
            opposite_diagonal_product = matrix[0][1] * matrix[1][0]
            determinant_value = float(main_diagonal_product - opposite_diagonal_product)
        validate_scalar(determinant_value, 'determinant (possible overflow)')
        if should_record_steps:
            steps = []
            record_step(steps, 'Starting matrix', matrix)
            description = '1x1 determinant is its sole entry' if matrix_size == 1 else '2x2 determinant = a*d - b*c'
            record_step(steps, f'{description} = {format_number(determinant_value)}', matrix)
            return CalculationResult(determinant_value, steps)
        return determinant_value
    elimination_result = eliminate(matrix, record_steps=should_record_steps)
    upper_triangular_matrix, row_swap_count, pivot_column_indices = elimination_result.value if should_record_steps else elimination_result
    if len(pivot_column_indices) < matrix_size:
        determinant_value = 0.0
        description = 'Missing pivot at tolerance: determinant = 0'
    else:
        determinant_value = -1.0 if row_swap_count % 2 else 1.0
        for diagonal_index in range(matrix_size):
            determinant_value *= upper_triangular_matrix[diagonal_index][diagonal_index]
        validate_scalar(determinant_value, 'determinant (possible overflow)')
        diagonal_factors = ' * '.join((format_number(upper_triangular_matrix[diagonal_index][diagonal_index]) for diagonal_index in range(matrix_size)))
        description = f'det = (-1)^{row_swap_count} * ({diagonal_factors}) = {format_number(determinant_value)}; {row_swap_count} row swap(s)'
    if should_record_steps:
        record_step(elimination_result.steps, description, upper_triangular_matrix)
        return CalculationResult(determinant_value, elimination_result.steps)
    return determinant_value
