import re
import sys
import numpy as np
import cmath
import csv

# Constants
Z_SOURCE = 50  # Assuming the source impedanceedance Rs is 50 Ohms if not specified in the file

def parse_net_file(file_path):
    # Parse the input file (as already provided in your code, unchanged)
    with open(file_path, 'r') as file:
        data = file.read().splitlines()

    circuit_data = []
    terms_data = {}
    output_data = []
    current_block = None

    for line in data:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '<CIRCUIT>' in line:
            current_block = 'CIRCUIT'
        elif '</CIRCUIT>' in line:
            current_block = None
        elif '<TERMS>' in line:
            current_block = 'TERMS'
        elif '</TERMS>' in line:
            current_block = None
        elif '<OUTPUT>' in line:
            current_block = 'OUTPUT'
        elif '</OUTPUT>' in line:
            current_block = None
        elif current_block == 'CIRCUIT' and current_block:
            circuit_data.append(line)
        elif current_block == 'TERMS' and current_block:
            pairs = line.split()
            for pair in pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    try:
                        # If the key is 'Nfreqs', we need to ensure it is stored as an integer
                        if key.strip() == 'Nfreqs':
                            terms_data[key.strip()] = int(float(value.strip()))  # Convert to integer
                        else:
                            terms_data[key.strip()] = float(value.strip())
                    except ValueError:
                        terms_data[key.strip()] = value.strip()
        # Adjust the output_data parsing
        elif current_block == 'OUTPUT' and current_block:
            parts = line.split()
            # If the output variable has no unit (like 'Av' or 'Ai'), manually add 'L'
            if len(parts) == 1:
                output_data.append((parts[0], 'L'))  # Now 'Av' and 'Ai' have 'L' as unit
            elif len(parts) == 2:
                output_data.append((parts[0], parts[1]))
            else:
                print(f"Warning: Unexpected output format in line: {line}")

    return circuit_data, terms_data, output_data

def compute_abcd_matrix(frequency, component):
    pattern = r'n1\s*=\s*(\d+)\s+n2\s*=\s*(\d+)\s+(R|L|C|G)\s*=\s*([0-9.e+-]+)'
    match = re.match(pattern, component.strip())
    if not match:
        print(f"Component format error or unmatched component: '{component}'")
        return None

    node1, node2, type, value = match.groups()
    value = float(value)
    
    print(value)
    print(node1, node2, type, value)

    if type == 'R':
        impedance = value 
    elif type == 'L':
        impedance = 2j * np.pi * frequency * value
    elif type == 'C':
        impedance = 1/(2j * np.pi * frequency * value)
    elif type == 'G':
        impedance = 1/value 
    else:
        raise ValueError(f"Invalid component type: {type}")
    
    # SORT IN ASCENDING N1, N2 ORDER
    # SIMPLIFY PARALLEL NODES 
        
    if node2 == '0':
        return np.array([[1, 0], [1/impedance, 1]])
    elif int(node2) == int(node1) + 1:
        return np.array([[1, impedance], [0, 1]])
    else:
        raise ValueError(f"Invalid component nodes: {node1}, {node2}")

def cascade_matrices(matrices):
    result = np.identity(2, dtype=complex)  # Ensure it's a complex type to handle inductors and capacitors
    for matrix in matrices:
        if matrix is not None:
            result = np.dot(result, matrix)
        else:
            print("Invalid matrix skipped")
    return result

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

def format_all_results(frequencies, output_structure):
    formatted_results = []
    for i, f in enumerate(frequencies):
        result = {'Freq': f"{f:.3e}"}
        for key in output_structure:
            if key not in ['Freq']:  
                result[f'Re({key})'] = f"{output_structure[key][i].real:.3e}"
                result[f'Im({key})'] = f"{output_structure[key][i].imag:.3e}"
        formatted_results.append(result)
    return formatted_results

def write_output_file(filename, output_data, all_results):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Freq']
        for name, unit in output_data:
            if unit != 'L':  
                fieldnames.extend([f'Re({name})', f'Im({name})'])
            else:  
                fieldnames.append(f'Re({name})')
                fieldnames.append(f'Im({name})')

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        units_row = {'Freq': 'Hz'}
        for name, unit in output_data:
            if unit != 'L':
                units_row[f'Re({name})'] = unit
                units_row[f'Im({name})'] = unit
            else:
                units_row[f'Re({name})'] = 'L'
                units_row[f'Im({name})'] = 'L'
        writer.writerow(units_row)
        for result in all_results:
            writer.writerow(result)

def main(input_file, output_file):
    # Parse the circuit file
    circuit_data, terms_data, output_data = parse_net_file(input_file)
    
    if 'LFstart' in terms_data and 'LFend' in terms_data:
            # Logarithmic sweep
            f_start = terms_data['LFstart']
            f_end = terms_data['LFend']
            frequencies = np.logspace(np.log10(f_start), np.log10(f_end), num=terms_data['Nfreqs'])
    else:
        # Linear or default frequency sweep
        f_start = terms_data.get('Fstart', 1)  # Default start frequency if not specified
        f_end = terms_data.get('Fend', 1e6)    # Default end frequency if not specified
        frequencies = np.linspace(f_start, f_end, num=terms_data.get('Nfreqs', 10))
    
    # Output structure preparation
    output_structure = {name: [] for name, _ in output_data}
    
    # Perform calculations for each frequency
    for f in frequencies:
        matrices = [compute_abcd_matrix(f, component) for component in circuit_data]
        total_matrix = cascade_matrices(matrices)
        
        # Calculate all output variables for this frequency
        results = calculate_output_variables(total_matrix, terms_data['VT'], terms_data.get('RS', 50), terms_data.get('ZL', 50))

        # Store the results in the output structure
        for key in results:
            output_structure[key].append(results[key])

    # Format and write the results to the output file
    all_results = format_all_results(frequencies, output_structure)
    write_output_file(output_file, output_data, all_results)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py input_file output_file")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])