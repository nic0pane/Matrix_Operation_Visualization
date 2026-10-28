from dataclasses import dataclass, field
from matrix import operations as matrix_operations
from matrix.determinant import matrix_determinant
from matrix.elimination import gaussian_elimination, gauss_jordan, matrix_rank, matrix_inverse
OPERATIONS = ('Addition A + B', 'Subtraction A - B', 'Multiplication A x B', 'Scalar multiplication', 'Transpose', 'Determinant', 'Gaussian elimination', 'Gauss-Jordan / RREF', 'Rank', 'Inverse', 'Eigenvalues and eigenvectors')
BINARY = OPERATIONS[:3]
STEP_FUNCTIONS = {
    'Determinant': matrix_determinant,
    'Gaussian elimination': gaussian_elimination,
    'Gauss-Jordan / RREF': gauss_jordan,
    'Rank': matrix_rank,
    'Inverse': matrix_inverse,
}

BINARY_OPERATION_FUNCTIONS = {
    'Addition A + B': matrix_operations.matrix_add,
    'Subtraction A - B': matrix_operations.matrix_sub,
    'Multiplication A x B': matrix_operations.matrix_multiply,
}

@dataclass
class Outcome:
    text: str
    explanation: str
    steps: list = field(default_factory=list)
    plot_kind: str = 'message'
    matrix: object = None
    intermediate: object = None
    determinant: object = None
    eigen: object = None

def execute(operation, selected, read_matrix, read_scalar):
    #read_matrix('A'/'B') and read_scalar() are lazy callbacks.
    if operation not in OPERATIONS:
        raise matrix_operations.MatrixError('Unknown operation')
    if selected not in ('A', 'B'):
        raise matrix_operations.MatrixError('Select A or B')
    calculation_steps = []
    determinant_value = None
    eigen_decomposition_result = None
    intermediate_matrix = None
    plot_kind = 'transformation'
    if operation in BINARY:
        matrix_a, matrix_b = (read_matrix('A'), read_matrix('B'))
        operation_function = BINARY_OPERATION_FUNCTIONS[operation]
        calculation_value = operation_function(matrix_a, matrix_b)
        visualization_matrix = calculation_value
        explanation = 'The result matrix is plotted when it is 2x2.'
        if operation == 'Multiplication A x B':
            explanation = 'Column-vector convention: (AB)v = A(Bv). Apply B first, then A.'
            if matrix_operations.matrix_shape(matrix_a) == (2, 2) and matrix_operations.matrix_shape(matrix_b) == (2, 2):
                intermediate_matrix = matrix_b
            elif matrix_operations.matrix_shape(calculation_value) == (2, 2):
                explanation += ' The plot shows only AB; intermediate spaces are not both 2D.'
    else:
        visualization_matrix = read_matrix(selected)
        explanation = f'Using matrix {selected}. '
        if operation in STEP_FUNCTIONS:
            calculation_result = STEP_FUNCTIONS[operation](visualization_matrix, record_steps=True)
            calculation_value, calculation_steps = (calculation_result.value, calculation_result.steps)
            if operation == 'Determinant':
                determinant_value = calculation_value
                plot_kind = 'determinant'
                explanation += 'Absolute determinant is area scaling in 2D; its sign describes orientation.'
            elif operation in ('Gaussian elimination', 'Gauss-Jordan / RREF', 'Rank'):
                plot_kind = 'message'
                explanation += 'Use Previous / Next to inspect row operations. Pivots use absolute tolerance 1e-12.'
            else:
                visualization_matrix = calculation_value
                explanation += 'Gauss-Jordan reduces [M | I] to [I | inverse]. The plot shows the inverse map.'
        elif operation == 'Scalar multiplication':
            calculation_value = matrix_operations.scalar_multiply(visualization_matrix, read_scalar())
            visualization_matrix = calculation_value
            explanation += 'The plot shows the resulting matrix as a linear map.'
        elif operation == 'Transpose':
            calculation_value = matrix_operations.matrix_transpose(visualization_matrix)
            visualization_matrix = calculation_value
            explanation += 'Rows and columns are interchanged; the plot shows the transpose.'
        else:
            eigen_decomposition_result = matrix_operations.eigen_decomposition(visualization_matrix)
            eigenvalues, eigenvectors = eigen_decomposition_result
            eigenpair_descriptions = [
                f'Pair {eigenpair_index + 1}: lambda = {matrix_operations.format_number(eigenvalues[eigenpair_index])}\n' + matrix_operations.matrix_to_str(
                    [[component] for component in eigenvectors[:, eigenpair_index]],
                )
                 for eigenpair_index in range(len(eigenvalues))
            ]
            formatted_result = '\n\n'.join(eigenpair_descriptions)
            explanation += 'Each displayed vector is paired with its eigenvalue from one decomposition. '
            explanation += 'Repeated eigenvalues do not guarantee independent eigenvectors.'
            return Outcome(
                formatted_result,
                explanation,
                plot_kind='eigen',
                matrix=visualization_matrix,
                eigen=eigen_decomposition_result,
            )
    formatted_result = matrix_operations.matrix_to_str(calculation_value) if isinstance(calculation_value, (list, tuple)) else matrix_operations.format_number(calculation_value)
    return Outcome(
        text=formatted_result,
        explanation=explanation,
        steps=calculation_steps,
        plot_kind=plot_kind,
        matrix=visualization_matrix,
        intermediate=intermediate_matrix,
        determinant=determinant_value,
        eigen=eigen_decomposition_result,
    )
