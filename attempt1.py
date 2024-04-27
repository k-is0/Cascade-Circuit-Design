import numpy as np
import re
import sys
import cmath

def parse_net_file(file_path):
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
                        terms_data[key.strip()] = float(value.strip())
                    except ValueError:
                        terms_data[key.strip()] = value.strip()
        elif current_block == 'OUTPUT' and current_block:
            parts = line.split()
            if len(parts) >= 2:
                output_data.append((parts[0], parts[1]))
            else:
                print(f"Warning: Unexpected output format in line: {line}")

    return circuit_data, terms_data, output_data

def abcd_for_component(component):
    """ Computes the ABCD matrix for the given component described by a line in the CIRCUIT block. """
    match = re.match(r'n1=(\d+) n2=(\d+) (R|L|C)=(.+)', component)
    if not match:
        return None, None, None

    node1, node2, type, value = match.groups()
    value = float(value)
    
    try:
        if type == 'R':
            # Series resistance
            return np.array([[1, value], [0, 1]]), node1, node2
        elif type == 'L':
            # Series inductance (jωL assumed ω=1 for simplicity)
            return np.array([[1, complex(0, value)], [0, 1]]), node1, node2
        elif type == 'C':
            # Shunt capacitance (1/jωC assumed ω=1 for simplicity)
            return np.array([[1, 0], [complex(0, -1/value), 1]]), node1, node2
    except Exception as e:
        print(f"Error computing ABCD matrix for component: {component}. Error: {str(e)}")
        return None, None, None

def cascade_matrices(matrices):
    """ Cascades a list of ABCD matrices. """
    result = np.array([[1, 0], [0, 1]])
    for matrix in matrices:
        result = np.dot(result, matrix)
    return result

def format_complex(c):
    """ Formats a complex number for output. """
    return f"{c.real:.3e}, {c.imag:.3e}"

def write_output_file(output_file, output_data, results):
    """ Writes the output data to a .csv file. """
    with open(output_file, 'w') as file:
        try:
            file.write(", ".join([name for name, unit in output_data]) + '\n')
            file.write(", ".join([unit for name, unit in output_data]) + '\n')
            file.write(", ".join([format_complex(results.get(name, 0)) for name, unit in output_data]) + '\n')
        except Exception as e:
            print(f"Error writing output file: {str(e)}")


def main(input_file, output_file):
    try:
        circuit_data, terms_data, output_data = parse_net_file(input_file)
    except Exception as e:
        print(f"Error parsing input file: {str(e)}")
        return

    matrices = []
    
    # Compute the ABCD matrices for each component and cascade them
    for component in circuit_data:
        matrix, n1, n2 = abcd_for_component(component)
        if matrix is not None:
            matrices.append(matrix)

    total_matrix = cascade_matrices(matrices)
    
    # Calculate the output variables (example placeholders)
    results = {
        'Vin': complex(1, 0),  # Placeholder for Vin calculation
        'Vout': total_matrix[0, 0],  # Simplified example
        'Iin': total_matrix[1, 1],  # Simplified example
        'Iout': total_matrix[1, 0]  # Simplified example
    }
    
    # Write results to output file
    write_output_file(output_file, output_data, results)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py input_file output_file")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    main(input_file, output_file)