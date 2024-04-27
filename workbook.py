# import numpy as np
# import re
# import sys
# import cmath

# def parse_net_file(file_path):
#     with open(file_path, 'r') as file:
#         data = file.read().splitlines()

#     circuit_data = []
#     terms_data = {}
#     output_data = []
#     current_block = None

#     for line in data:
#         line = line.strip()
#         if not line or line.startswith('#'):
#             continue
        
#         if '<CIRCUIT>' in line:
#             current_block = 'CIRCUIT'
#         elif '</CIRCUIT>' in line:
#             current_block = None
#         elif '<TERMS>' in line:
#             current_block = 'TERMS'
#         elif '</TERMS>' in line:
#             current_block = None
#         elif '<OUTPUT>' in line:
#             current_block = 'OUTPUT'
#         elif '</OUTPUT>' in line:
#             current_block = None
#         elif current_block == 'CIRCUIT' and current_block:
#             circuit_data.append(line)
#         elif current_block == 'TERMS' and current_block:
#             pairs = line.split()
#             for pair in pairs:
#                 if '=' in pair:
#                     key, value = pair.split('=', 1)
#                     try:
#                         terms_data[key.strip()] = float(value.strip())
#                     except ValueError:
#                         terms_data[key.strip()] = value.strip()
#         elif current_block == 'OUTPUT' and current_block:
#             parts = line.split()
#             if len(parts) >= 2:
#                 output_data.append((parts[0], parts[1]))
#             else:
#                 print(f"Warning: Unexpected output format in line: {line}")

#     return circuit_data, terms_data, output_data

# def abcd_for_component(component):
#     """ Computes the ABCD matrix for the given component described by a line in the CIRCUIT block. """
#     match = re.match(r'n1=(\d+) n2=(\d+) (R|L|C)=(.+)', component)
#     if not match:
#         return None, None, None

#     node1, node2, type, value = match.groups()
#     value = float(value)
    
#     try:
#         if type == 'R':
#             # Series resistance
#             return np.array([[1, value], [0, 1]]), node1, node2
#         elif type == 'L':
#             # Series inductance (jωL assumed ω=1 for simplicity)
#             return np.array([[1, complex(0, value)], [0, 1]]), node1, node2
#         elif type == 'C':
#             # Shunt capacitance (1/jωC assumed ω=1 for simplicity)
#             return np.array([[1, 0], [complex(0, -1/value), 1]]), node1, node2
#     except Exception as e:
#         print(f"Error computing ABCD matrix for component: {component}. Error: {str(e)}")
#         return None, None, None

# def cascade_matrices(matrices):
#     """ Cascades a list of ABCD matrices. """
#     result = np.array([[1, 0], [0, 1]])
#     for matrix in matrices:
#         result = np.dot(result, matrix)
#     return result

# def format_complex(c):
#     """ Formats a complex number for output. """
#     return f"{c.real:.3e}, {c.imag:.3e}"

# def write_output_file(output_file, output_data, results):
#     """ Writes the output data to a .csv file. """
#     with open(output_file, 'w') as file:
#         try:
#             file.write(", ".join([name for name, unit in output_data]) + '\n')
#             file.write(", ".join([unit for name, unit in output_data]) + '\n')
#             file.write(", ".join([format_complex(results.get(name, 0)) for name, unit in output_data]) + '\n')
#         except Exception as e:
#             print(f"Error writing output file: {str(e)}")

# def main(input_file, output_file):
#     try:
#         circuit_data, terms_data, output_data = parse_net_file(input_file)
#     except Exception as e:
#         print(f"Error parsing input file: {str(e)}")
#         return

#     matrices = []
    
#     # Compute the ABCD matrices for each component and cascade them
#     for component in circuit_data:
#         matrix, n1, n2 = abcd_for_component(component)
#         if matrix is not None:
#             matrices.append(matrix)

#     total_matrix = cascade_matrices(matrices)
    
#     # Calculate the output variables (example placeholders)
#     results = {
#         'Vin': complex(1, 0),  # Placeholder for Vin calculation
#         'Vout': total_matrix[0, 0],  # Simplified example
#         'Iin': total_matrix[1, 1],  # Simplified example
#         'Iout': total_matrix[1, 0]  # Simplified example
#     }
    
#     # Write results to output file
#     write_output_file(output_file, output_data, results)

# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python script.py input_file output_file")
#         sys.exit(1)
#     input_file = sys.argv[1]
#     output_file = sys.argv[2]
#     main(input_file, output_file)
    
"""-----------------------------------------------------------------------------------------------------------------"""
    
import re
import sys
import numpy as np
import cmath
import csv

# Constants
Z_SOURCE = 50  # Assuming the source impedance Rs is 50 Ohms if not specified in the file

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

def compute_abcd_matrix(frequency, component):
    # Handling variations in component formatting
    pattern = r'n1\s*=\s*(\d+)\s+n2\s*=\s*(\d+)\s+(R|L|C)\s*=\s*(.+)'
    match = re.match(pattern, component)
    if match:
        node1, node2, type, value = match.groups()
        value = float(value)
        
        if type == 'R':
            return np.array([[1, value], [0, 1]])
        elif type == 'L':
            return np.array([[1, complex(0, 2 * np.pi * frequency * value)], [0, 1]])
        elif type == 'C':
            return np.array([[1, 0], [complex(0, -1 / (2 * np.pi * frequency * value)), 1]])
    else:
        print(f"Component format error: {component}")
        return None

def cascade_matrices(matrices):
    result = np.identity(2)
    for matrix in matrices:
        result = np.dot(result, matrix)
    return result

def calculate_impedance(abcd_matrix, zl):
    a, b, c, d = abcd_matrix[0, 0], abcd_matrix[0, 1], abcd_matrix[1, 0], abcd_matrix[1, 1]
    zin = (a * zl + b) / (c * zl + d)
    return zin

def calculate_vin_iin_vout_iout(abcd_matrix, zin, zl, vt):
    a, b, c, d = abcd_matrix[0, 0], abcd_matrix[0, 1], abcd_matrix[1, 0], abcd_matrix[1, 1]
    vin = vt / (zin + Z_SOURCE)
    iin = vin / zin
    vout = (a * vin) + (b * iin)
    iout = (c * vin) + (d * iin)
    return vin, iin, vout, iout

def format_all_results(frequencies, output_structure):
    # Function to format the output according to the provided example, including all variables
    formatted_results = []
    for i, f in enumerate(frequencies):
        formatted_results.append({
            'Freq': f"{f:.2f}",
            'Re(Vin)': f"{output_structure['Vin'][i].real:.3e}",
            'Im(Vin)': f"{output_structure['Vin'][i].imag:.3e}",
            # ... format other variables similarly
        })
    return formatted_results

def write_output_file(output_file, output_data, all_results):
    # Writes the output data to a .csv file, following the structure of output_data
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name for name, _ in output_data])  # Header
        writer.writerow([unit for _, unit in output_data])  # Units
        for result in all_results:
            writer.writerow(result.values())

def main(input_file, output_file):
    # Parse the circuit file
    circuit_data, terms_data, output_data = parse_net_file(input_file)
    
    # Obtain the frequency range and points for analysis
    f_start = terms_data['Fstart']
    f_end = terms_data['Fend']
    n_freqs = int(terms_data['Nfreqs'])  # Explicitly convert to integer
    
    # Frequency sweep
    frequencies = np.logspace(np.log10(f_start), np.log10(f_end), num=n_freqs)
    
    # Output structure preparation
    output_structure = {name: [] for name, _ in output_data}
    
    # Perform calculations for each frequency
    for f in frequencies:
        matrices = [compute_abcd_matrix(f, component) for component in circuit_data]
        total_matrix = cascade_matrices(matrices)
        
        # Calculate Zin, Vin, Iin, Vout, Iout for this frequency
        zl = terms_data.get('ZL', 50)  # Load impedance
        zin = calculate_impedance(total_matrix, zl)
        vin, iin, vout, iout = calculate_vin_iin_vout_iout(total_matrix, zin, zl, terms_data['VT'])

        # Store the results in the output structure
        output_structure['Vin'].append(vin)
        output_structure['Iin'].append(iin)
        # ... Add other variables ...

    # Format and write the results to the output file
    all_results = format_all_results(frequencies, output_structure)
    write_output_file(output_file, output_data, all_results)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py input_file output_file")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])



# Define the main function to process the input file and write to the output file



# # ... [Existing imports and code] ...

# def calculate_impedance(abcd_matrix, zs, zl):
#     a, b, c, d = abcd_matrix[0, 0], abcd_matrix[0, 1], abcd_matrix[1, 0], abcd_matrix[1, 1]
#     zin = (a * zl + b) / (c * zl + d)
#     zout = (d * zs + b) / (c * zs + a)
#     return zin, zout

# def calculate_voltage_current_power(abcd_matrix, zin, zl, vt):
#     a, b, c, d = abcd_matrix[0, 0], abcd_matrix[0, 1], abcd_matrix[1, 0], abcd_matrix[1, 1]
#     vin = vt / (zin + 50)  # Assuming source impedance Rs is 50 Ohms
#     iin = vin / zin
#     vout = vin * a + iin * b
#     iout = vin * c + iin * d
#     pout = abs(vout * iout.conjugate())
#     return vin, iin, vout, iout, pout

# def compute_abcd_matrix(frequency, component):
#     # Frequency-dependent component calculations should be implemented here
#     # Use the existing 'abcd_for_component' function and update it to handle frequency
#     pass

# # ... [Existing code and definitions] ...

# def main(input_file, output_file):
#     # Parse the circuit file
#     circuit_data, terms_data, output_data = parse_net_file(input_file)

#     # Obtain the frequency range and number of points
#     f_start, f_end, n_freqs = terms_data['Fstart'], terms_data['Fend'], int(terms_data['Nfreqs'])
    
#     # Prepare a list to hold all frequency results
#     all_results = []

#     # Perform the frequency sweep
#     for f in log_frequency_sweep(f_start, f_end, n_freqs) if USE_LOG_SWEEP else np.linspace(f_start, f_end, n_freqs):
#         matrices = [compute_abcd_matrix(f, component) for component in circuit_data]
#         total_matrix = cascade_matrices(matrices)

#         # Assuming a Thevenin source with a voltage VT, which needs to be parsed from the input file
#         vt = terms_data['VT']
#         zl = terms_data.get('ZL', 50)  # Assuming a load impedance if not specified
        
#         # Calculate the impedances
#         zin, zout = calculate_impedance(total_matrix, 50, zl)  # Assuming source impedance Rs is 50 Ohms
        
#         # Calculate the voltages, currents, and power
#         vin, iin, vout, iout, pout = calculate_voltage_current_power(total_matrix, zin, zl, vt)
        
#         # Store results for this frequency
#         results = {
#             'Freq': f,
#             'Vin': vin,
#             'Iin': iin,
#             'Vout': vout,
#             'Iout': iout,
#             'Pin': vin * iin.conjugate(),
#             'Zout': zout,
#             'Pout': pout,
#             'Zin': zin,
#             'Av': vout / vin,
#             'Ai': iout / iin
#         }
        
#         all_results.append(results)

#     # Write results to the output file
#     write_output_file(output_file, output_data, all_results)

# # ... [Rest of the existing code] ...

# if __name__ == "__main__":
#     # Execute the main function with command-line arguments
#     main(sys.argv[1], sys.argv[2])


# import numpy as np
# import cmath
# import csv
# import re

# def parse_net_file(file_path):
#     # This function remains unchanged; it reads the input file and parses it into data blocks.
#     pass

# def compute_abcd_matrix(frequency, component):
#     # This function computes the ABCD matrix for each component considering its frequency-dependent behavior.
#     pass

# def format_complex(c):
#     # Formats a complex number for output in real and imaginary parts.
#     pass

# def write_output_file(output_file, output_data, all_results):
#     # Writes the output data to a .csv file.
#     pass

# def main(input_file, output_file):
#     circuit_data, terms_data, output_data = parse_net_file(input_file)

#     # Get frequency range from terms_data
#     f_start, f_end, n_freqs = terms_data['Fstart'], terms_data['Fend'], terms_data['Nfreqs']
#     frequencies = np.logspace(np.log10(f_start), np.log10(f_end), num=n_freqs) if USE_LOG_SWEEP else np.linspace(f_start, f_end, n_freqs)

#     # Output structure preparation
#     output_structure = {name: [] for name, unit in output_data}
#     output_structure['Freq'] = []

#     # Frequency sweep
#     for f in frequencies:
#         matrices = [compute_abcd_matrix(f, comp) for comp in circuit_data]
#         total_matrix = cascade_matrices(matrices)

#         # Perform calculations for Vin, Iin, Zin, etc. based on the total_matrix and terms_data.
#         # Placeholder for calculations (Assume functions like calculate_vin are defined elsewhere):
#         zin, zout = calculate_impedance(total_matrix, terms_data['ZS'], terms_data['ZL'])
#         vin, iin, vout, iout = calculate_vin_iin_vout_iout(total_matrix, zin, terms_data['VT'])
        
#         # Store the results in the output structure
#         output_structure['Freq'].append(f)
#         output_structure['Vin'].append(vin)
#         output_structure['Iin'].append(iin)
#         # ... Add other variables similarly ...

#     # Formatting output according to the required units and writing to file
#     all_results = format_all_results(output_structure)  # Assume this function formats the output structure
#     write_output_file(output_file, output_data, all_results)

# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python script.py input_file output_file")
#         sys.exit(1)

#     input_file, output_file = sys.argv[1], sys.argv[2]
#     main(input_file, output_file)
