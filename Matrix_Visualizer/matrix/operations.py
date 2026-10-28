#Basic list-based arithmetic, validation and NumPy eigen decomposition.

#Inputs are nonempty rectangular lists/tuples of finite real numbers.
#Functions never modify inputs. EPS is an absolute pivot tolerance.

import math
import numbers
from dataclasses import dataclass
import numpy as np
EPS = 1e-12

class MatrixError(ValueError):
    """Invalid input, incompatible dimensions or a failed calculation."""

@dataclass
class CalculationStep:
    description: str
    matrix: list

@dataclass
class CalculationResult:
    """Returned only when record_steps=True (or legacy verbose=True).

    value has the same type as the function's ordinary return value.
    Every step owns its own independent list-of-lists snapshot.
    """
    value: object
    steps: list

def record_step(steps, description, matrix):
    if steps is not None:
        steps.append(CalculationStep(description, [list(row) for row in matrix]))

def validate_scalar(value, name='scalar'):
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise MatrixError(f'{name} must be a finite real number')
    try:
        is_finite = math.isfinite(value)
    except (OverflowError, TypeError, ValueError):
        is_finite = False
    if not is_finite:
        raise MatrixError(f'{name} must be a finite real number')
    return value

def validate_matrix(matrix, name='matrix'):
    if not isinstance(matrix, (list, tuple)) or not matrix:
        raise MatrixError(f'{name} must be a non-empty list of rows')
    for row_index, row in enumerate(matrix):
        if not isinstance(row, (list, tuple)) or not row:
            raise MatrixError(f'{name}: row {row_index + 1} must be a non-empty list')
    column_count = len(matrix[0])
    for row_index, row in enumerate(matrix):
        if len(row) != column_count:
            raise MatrixError(f'{name} is not rectangular (row {row_index + 1})')
        for column_index, value in enumerate(row):
            validate_scalar(value, f'{name}[{row_index + 1},{column_index + 1}]')
    return (len(matrix), column_count)

def matrix_shape(matrix, name='matrix'):
    return validate_matrix(matrix, name)

def require_square(matrix, name='matrix'):
    row_count, column_count = validate_matrix(matrix, name)
    if row_count != column_count:
        raise MatrixError(f'{name} must be square, got {row_count}x{column_count}')
    return row_count

def format_number(value):
    #Display real or complex results without discarding imaginary parts.
    complex_value = complex(value)
    if complex_value.imag != 0:
        return f'{complex_value.real:.6g}{complex_value.imag:+.6g}j'
    real_part = complex_value.real
    if real_part == 0:
        return '0'
    if abs(real_part) < 1000000000.0 and real_part.is_integer():
        return str(int(real_part))
    return f'{real_part:.6g}'

def matrix_to_str(matrix):
    formatted_rows = []
    for row in matrix:
        formatted_rows.append([format_number(value) for value in row])
    column_widths = []
    for column_index in range(len(formatted_rows[0])):
        longest_cell_width = max((len(row[column_index]) for row in formatted_rows))
        column_widths.append(longest_cell_width)
    output_lines = []
    for formatted_row in formatted_rows:
        aligned_cells = []
        for formatted_value, column_width in zip(formatted_row, column_widths):
            aligned_cells.append(formatted_value.rjust(column_width))
        output_lines.append('[ ' + '  '.join(aligned_cells) + ' ]')
    return '\n'.join(output_lines)

def matrix_display(matrix, title=None):
    #Return formatted text, instead of printing as the original did.
    validate_matrix(matrix)
    return (str(title) + '\n' if title else '') + matrix_to_str(matrix)

def _validate_result_matrix(matrix):
    validate_matrix(matrix, 'result (possible numerical overflow)')
    return matrix

def _require_matching_shapes(first_matrix, second_matrix, operation_name):
    first_shape = validate_matrix(first_matrix, 'A')
    second_shape = validate_matrix(second_matrix, 'B')
    if first_shape != second_shape:
        raise MatrixError(f'Cannot {operation_name}: shapes {first_shape} and {second_shape} differ')
    return first_shape

def matrix_add(matrix_a, matrix_b):
    row_count, column_count = _require_matching_shapes(matrix_a, matrix_b, 'add')
    result_matrix = []
    for row_index in range(row_count):
        result_row = []
        for column_index in range(column_count):
            cell_sum = matrix_a[row_index][column_index] + matrix_b[row_index][column_index]
            result_row.append(cell_sum)
        result_matrix.append(result_row)
    return _validate_result_matrix(result_matrix)

def matrix_sub(matrix_a, matrix_b):
    row_count, column_count = _require_matching_shapes(matrix_a, matrix_b, 'subtract')
    result_matrix = []
    for row_index in range(row_count):
        result_row = []
        for column_index in range(column_count):
            cell_difference = matrix_a[row_index][column_index] - matrix_b[row_index][column_index]
            result_row.append(cell_difference)
        result_matrix.append(result_row)
    return _validate_result_matrix(result_matrix)

def scalar_multiply(matrix, scalar):
    row_count, column_count = validate_matrix(matrix)
    validate_scalar(scalar)
    scaled_matrix = []
    for row_index in range(row_count):
        scaled_row = []
        for column_index in range(column_count):
            scaled_value = scalar * matrix[row_index][column_index]
            scaled_row.append(scaled_value)
        scaled_matrix.append(scaled_row)
    return _validate_result_matrix(scaled_matrix)

def matrix_multiply(matrix_a, matrix_b):
    first_row_count, shared_dimension = validate_matrix(matrix_a, 'A')
    second_row_count, second_column_count = validate_matrix(matrix_b, 'B')
    if shared_dimension != second_row_count:
        raise MatrixError(f'Cannot multiply {first_row_count}x{shared_dimension} by {second_row_count}x{second_column_count}: A columns must equal B rows')
    product_matrix = []
    
    for row_index in range(first_row_count):
        product_row = []
        for column_index in range(second_column_count):
            component_products = []
            for shared_index in range(shared_dimension):
                component_product = matrix_a[row_index][shared_index] * matrix_b[shared_index][column_index]
                component_products.append(component_product)
            product_row.append(sum(component_products))
        product_matrix.append(product_row)
    return _validate_result_matrix(product_matrix)

def matrix_transpose(matrix):
    row_count, column_count = validate_matrix(matrix)
    transposed_matrix = []
    for column_index in range(column_count):
        transposed_row = []
        for row_index in range(row_count):
            transposed_row.append(matrix[row_index][column_index])
        transposed_matrix.append(transposed_row)
    return transposed_matrix

def eigen_decomposition(matrix):
    #Return (values, vectors); vectors[:, i] belongs to values[i].
    require_square(matrix)
    try:
        eigenvalues, eigenvectors = np.linalg.eig(np.array(matrix, dtype=float))
    except np.linalg.LinAlgError as error:
        raise MatrixError(f'Eigen decomposition failed: {error}') from error
    if not (np.isfinite(eigenvalues).all() and np.isfinite(eigenvectors).all()):
        raise MatrixError('Eigen decomposition produced non-finite results')
    return (eigenvalues, eigenvectors)

def eigen_values(matrix):
    return eigen_decomposition(matrix)[0]

def eigen_vectors(matrix):
    return eigen_decomposition(matrix)[1]
