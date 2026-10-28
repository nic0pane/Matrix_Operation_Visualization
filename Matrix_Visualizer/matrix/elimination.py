#Original partial-pivoting elimination, refactored to return snapshots.

#Default return signatures are preserved. record_steps=True returns a
#CalculationResult. Legacy verbose=True now means record steps, never print.

from .operations import (
    EPS,
    MatrixError,
    CalculationResult,
    record_step,
    format_number,
    require_square,
    validate_matrix,
)

def eliminate(matrix, verbose=False, jordan=False, pivot_cols=None, *, record_steps=False):
    row_count, column_count = validate_matrix(matrix)
    if pivot_cols is not None and (isinstance(pivot_cols, bool) or not isinstance(pivot_cols, int) or (not 0 <= pivot_cols <= column_count)):
        raise MatrixError(f'pivot_cols must be an integer between 0 and {column_count}')
    working_matrix = [[float(cell_value) for cell_value in row] for row in matrix]
    pivot_column_limit = column_count if pivot_cols is None else pivot_cols
    steps = [] if record_steps or verbose else None
    record_step(steps, 'Starting matrix', working_matrix)
    row_swap_count, pivot_column_indices, pivot_row_index = (0, [], 0)
    for pivot_column_index in range(pivot_column_limit):
        if pivot_row_index >= row_count:
            break
        selected_pivot_row_index = max(
            range(pivot_row_index, row_count),
            key=lambda target_row_index: abs(working_matrix[target_row_index][pivot_column_index]),
        )
        if abs(working_matrix[selected_pivot_row_index][pivot_column_index]) < EPS:
            record_step(steps,f'Column {pivot_column_index + 1}: no pivot above tolerance; skip',working_matrix)
            continue
        if selected_pivot_row_index != pivot_row_index:
            working_matrix[pivot_row_index], working_matrix[selected_pivot_row_index] = (working_matrix[selected_pivot_row_index], working_matrix[pivot_row_index])
            row_swap_count += 1
            record_step(steps,f'Swap R{pivot_row_index + 1} <-> R{selected_pivot_row_index + 1}',working_matrix)
        if jordan:
            pivot_value = working_matrix[pivot_row_index][pivot_column_index]
            if pivot_value != 1.0:
                working_matrix[pivot_row_index] = [row_value / pivot_value for row_value in working_matrix[pivot_row_index]]
                working_matrix[pivot_row_index][pivot_column_index] = 1.0
                validate_matrix(working_matrix, 'elimination result (possible overflow)')
                record_step(steps,f'R{pivot_row_index + 1} = R{pivot_row_index + 1} / {format_number(pivot_value)}',working_matrix,)
        rows_to_eliminate = range(row_count) if jordan else range(pivot_row_index + 1, row_count)
        for target_row_index in rows_to_eliminate:
            if target_row_index == pivot_row_index:
                continue
            # A small factor can still have a large effect in another column.
            elimination_factor = working_matrix[target_row_index][pivot_column_index] / working_matrix[pivot_row_index][pivot_column_index]
            if elimination_factor == 0:
                continue
            working_matrix[target_row_index] = [
                target_value - elimination_factor * pivot_row_value
                 for target_value, pivot_row_value in zip(working_matrix[target_row_index], working_matrix[pivot_row_index])
            ]
            working_matrix[target_row_index][pivot_column_index] = 0.0
            validate_matrix(working_matrix, 'elimination result (possible overflow)')
            record_step(steps,f'R{target_row_index + 1} = R{target_row_index + 1} - ({format_number(elimination_factor)}) * R{pivot_row_index + 1}',working_matrix)
        pivot_column_indices.append(pivot_column_index)
        pivot_row_index += 1

    # Clean only the searched block; preserve small values in an inverse block.
    for target_row_index in range(pivot_row_index, row_count):
        for pivot_column_index in range(pivot_column_limit):
            if abs(working_matrix[target_row_index][pivot_column_index]) < EPS:
                working_matrix[target_row_index][pivot_column_index] = 0.0
    record_step(steps, 'Finished (absolute pivot tolerance = 1e-12)', working_matrix)
    elimination_data = (working_matrix, row_swap_count, pivot_column_indices)
    return CalculationResult(elimination_data, steps) if steps is not None else elimination_data

def _calculate_elimination_operation(matrix, verbose, record_steps, jordan=False, rank=False):
    elimination_result = eliminate(matrix, jordan=jordan, record_steps=record_steps or verbose)
    has_recorded_steps = isinstance(elimination_result, CalculationResult)
    elimination_data = elimination_result.value if has_recorded_steps else elimination_result
    reduced_matrix, _, pivot_column_indices = elimination_data
    operation_value = len(pivot_column_indices) if rank else reduced_matrix
    if has_recorded_steps:
        if rank:
            record_step(
                elimination_result.steps,
                f'Pivot columns: {[pivot_column_index + 1 for pivot_column_index in pivot_column_indices]}; rank = {operation_value}',
                reduced_matrix,
            )
        return CalculationResult(operation_value, elimination_result.steps)
    return operation_value

def gaussian_elimination(matrix, verbose=False, *, record_steps=False):
    return _calculate_elimination_operation(matrix, verbose, record_steps)

def gauss_jordan(matrix, verbose=False, *, record_steps=False):
    return _calculate_elimination_operation(matrix, verbose, record_steps, jordan=True)

def matrix_rank(matrix, verbose=False, *, record_steps=False):
    return _calculate_elimination_operation(matrix, verbose, record_steps, rank=True)

def matrix_inverse(matrix, verbose=False, *, record_steps=False):
    matrix_size = require_square(matrix)
    augmented_matrix = [
        list(map(float, row)) + [float(row_index == column_index) for column_index in range(matrix_size)]
         for row_index, row in enumerate(matrix)
    ]

    should_record_steps = record_steps or verbose
    elimination_result = eliminate(augmented_matrix,jordan=True,pivot_cols=matrix_size,record_steps=should_record_steps)
    reduced_augmented_matrix, _, pivot_column_indices = elimination_result.value if should_record_steps else elimination_result
    
    if len(pivot_column_indices) < matrix_size:
        raise MatrixError('Matrix is singular at the pivot tolerance; no inverse exists')
    inverse_matrix = [row[matrix_size:] for row in reduced_augmented_matrix]
    
    if should_record_steps:
        elimination_result.steps[0].description = 'Starting augmented matrix [M | I]'
        record_step(
            elimination_result.steps,
            'Left block is I; extract the right block as the inverse',
            inverse_matrix,
        )
        return CalculationResult(inverse_matrix, elimination_result.steps)
    return inverse_matrix
