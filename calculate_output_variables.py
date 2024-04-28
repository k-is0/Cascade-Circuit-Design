import numpy as np

def calculate_output_variables(abcd_matrix, vt, rs, rl):
    a, b, c, d = abcd_matrix[0, 0], abcd_matrix[0, 1], abcd_matrix[1, 0], abcd_matrix[1, 1]
    zin = (a * rl + b) / (c * rl + d)  # Input impedances seen looking into the source
    zout = (d * rs + b) / (c * rs + a)  # Output impedances seen looking into the load
    
    vin = vt / (zin + rs)
    iin = vin / zin
    vout = a * vin + b * iin
    iout = c * vin + d * iin
    
    pin = vin * np.conj(iin)  # Power input
    pout = vout * np.conj(iout)  # Power output
    av = vout / vin  # Voltage gain
    ai = iout / iin  # Current gain
    
    return {
        'Vin': vin, 'Vout': vout, 'Iin': iin, 'Iout': iout, 
        'Pin': pin, 'Zin': zin, 'Pout': pout, 'Zout': zout,
        'Av': av, 'Ai': ai
    }