import numpy as np

def impedance_matrix(frequency, n1, n2, component_type, value):
    # Convert n1 and n2 to integers to handle node connections properly
    n1, n2 = int(n1), int(n2)
    
    frequency = float(frequency)
    value = float(value)

    # Calculate the impedance or admittance based on component type
    if component_type == 'R':
        impedance = value
    elif component_type == 'L':
        impedance = 2j * np.pi * frequency * value
    elif component_type == 'C':
        impedance = -1j / (2 * np.pi * frequency * value)
    elif component_type == 'G':
        admittance = value
        impedance = 1 / admittance  # Convert conductance to resistance for series calculation
    else:
        raise ValueError(f"Invalid component type: {component_type}")
    
    # Determine if the component is shunt or series and return the appropriate matrix
    if n2 == 0:
        if component_type == 'G':  # Handling for shunt conductance
            return np.array([[1, 0], [impedance, 1]], dtype=complex)
        else:  # For R, L, C shunt components
            return np.array([[1, 0], [1/impedance, 1]], dtype=complex)
    else:
        # Handle components between any two nodes, including series conductance
        return np.array([[1, impedance], [0, 1]], dtype=complex)

def cascade_matrices(matrices):
    result = np.identity(2, dtype=complex)  # Ensure it's complex type to handle inductors and capacitors
    for matrix in matrices:
        if matrix is not None:
            result = np.dot(result, matrix)
        else:
            print("Invalid matrix skipped")
    return result

def calculate_output_variables(abcd_matrix, vt, rs, rl):
    a, b, c, d = abcd_matrix.flatten()
    zin = (a * rl + b) / (c * rl + d)  # Input impedances seen looking into the source
    zout = (d * rs + b) / (c * rs + a)  # Output impedances seen looking into the load
    
    av = rl / ((a * rl) + b) # Voltage gain
    ai = 1 / ((c * rl) + d)  # Current gain
    ap = av * ai.conj() # Power gain
    
    vin = vt * zin / (zin + rs)  # Voltage input
    iin = vt / (zin + rs) # vin / zin 
    vout = vin * av  # Voltage output
    iout = iin * ai  # Current output
    pin = vin * iin.conj()  # Power input
    pout = pin * ap  # Power output
    
    return {
        'Vin': vin, 'Vout': vout, 'Iin': iin, 'Iout': iout, 
        'Pin': pin, 'Zin': zin, 'Pout': pout, 'Zout': zout,
        'Av': av, 'Ai': ai,
    }