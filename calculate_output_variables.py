import numpy as np

def calculate_output_variables(abcd_matrix, vt, rs, rl):
    a, b, c, d = abcd_matrix[0, 0], abcd_matrix[0, 1], abcd_matrix[1, 0], abcd_matrix[1, 1]
    zin = (a * rl + b) / (c * rl + d)  # Input impedances seen looking into the source
    zout = (d * rs + b) / (c * rs + a)  # Output impedances seen looking into the load
    
    # av = rl / ((a * rl) + b)
    # ai = 1 / ((c * rl) + d)
    
    vin = vt * zin / (zin + rs)  # Voltage input
    iin = vt / (zin + rs) # vin / zin 
    # vout = av * vin  # Voltage output
    # iout = ai * iin  # Current output
    # vout = (a * vin) + (b * iin)
    # iout = (c * vin) + (d * iin)
    
    matrix = np.matrix([[a, b], [c, d]])
    inverse_matrix = np.linalg.inv(matrix)
    vector = np.array([vin, iin])
    output_vector = np.array(np.dot(inverse_matrix, vector))
    vout = output_vector[0]
    iout = 0 if len(output_vector) < 2 else output_vector[1]
    
    
    pin = vin * np.conj(iin)  # Power input
    pout = vout * np.conj(iout)  # Power output
    av = vout / vin  # Voltage gain
    ai = iout / iin  # Current gain
    
    return {
        'Vin': vin, 'Vout': vout, 'Iin': iin, 'Iout': iout, 
        'Pin': pin, 'Zin': zin, 'Pout': pout, 'Zout': zout,
        'Av': av, 'Ai': ai
    }