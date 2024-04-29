import numpy as np

def calculate_output_variables(abcd_matrix, vt, rs, rl, output_data):
    a, b, c, d = abcd_matrix.flatten()
    zin = (a * rl + b) / (c * rl + d)  # Input impedances seen looking into the source
    zout = (d * rs + b) / (c * rs + a)  # Output impedances seen looking into the load
    
    av = rl / ((a * rl) + b)
    ai = 1 / ((c * rl) + d)
    ap = av * ai.conj()
    
    vin = vt * zin / (zin + rs)  # Voltage input
    iin = vt / (zin + rs) # vin / zin 
    vout = vin * av  # Voltage output
    iout = iin * ai  # Current output
    pin = vin * iin.conj()  # Power input
    pout = pin * ap  # Power output
    
    
    return {
        'Vin': vin, 'Vout': vout, 'Iin': iin, 'Iout': iout, 
        'Pin': pin, 'Zin': zin, 'Pout': pout, 'Zout': zout,
        'Av': av, 'Ai': ai
    }