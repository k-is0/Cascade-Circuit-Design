import numpy as np

def cascade_matrices(matrices):
    result = np.identity(2, dtype=complex)  # Ensure it's a complex type to handle inductors and capacitors
    for matrix in matrices:
        if matrix is not None:
            result = np.dot(result, matrix)
        else:
            print("Invalid matrix skipped")
    return result
