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
    pattern = r'n1\s*=\s*(\d+)\s+n2\s*=\s*(\d+)\s+(R|L|C)\s*=\s*([0-9.e+-]+)'
    match = re.match(pattern, component.strip())
    if not match:
        print(f"Component format error or unmatched component: '{component}'")
        return None

    node1, node2, type, value = match.groups()
    value = float(value)

    if type == 'R':
        return np.array([[1, value], [0, 1]])
    elif type == 'L':
        return np.array([[1, complex(0, 2 * np.pi * frequency * value)], [0, 1]])
    elif type == 'C':
        return np.array([[1, 0], [complex(0, -1 / (2 * np.pi * frequency * value)), 1]])

    return None  # If none of the types match, return None

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
    zin = (a * rl + b) / (c * rl + d)  # Input impedance seen looking into the source
    zout = (d * rs + b) / (c * rs + a)  # Output impedance seen looking into the load
    
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
    
# import re
# import sys
# import numpy as np
# import cmath
# import csv

# # Constants
# Z_SOURCE = 50  # Assuming the source impedance Rs is 50 Ohms if not specified in the file

# def parse_net_file(file_path):
#     # Parse the input file (as already provided in your code, unchanged)
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
#                         # If the key is 'Nfreqs', we need to ensure it is stored as an integer
#                         if key.strip() == 'Nfreqs':
#                             terms_data[key.strip()] = int(float(value.strip()))  # Convert to integer
#                         else:
#                             terms_data[key.strip()] = float(value.strip())
#                     except ValueError:
#                         terms_data[key.strip()] = value.strip()
#         # Adjust the output_data parsing
#         elif current_block == 'OUTPUT' and current_block:
#             parts = line.split()
#             # If the output variable has no unit (like 'Av' or 'Ai'), manually add 'L'
#             if len(parts) == 1:
#                 output_data.append((parts[0], 'L'))  # Now 'Av' and 'Ai' have 'L' as unit
#             elif len(parts) == 2:
#                 output_data.append((parts[0], parts[1]))
#             else:
#                 print(f"Warning: Unexpected output format in line: {line}")

#     return circuit_data, terms_data, output_data

# def build_circuit_graph(circuit_data):
#     graph = {}
#     for component in circuit_data:
#         parsed = parse_component(component)
#         if parsed is not None:  # Skip lines that don't match the component pattern
#             n1, n2, _, _ = parsed
#             graph.setdefault(n1, []).append(n2)
#     return graph


# def topological_sort_util(node, visited, stack, graph):
#     visited.add(node)
#     for neighbour in graph.get(node, []):
#         if neighbour not in visited:
#             topological_sort_util(neighbour, visited, stack, graph)
#     stack.insert(0, node)  # insert at the beginning to avoid reversing later

# def topological_sort(graph, start):
#     visited = set()
#     stack = []

#     # Call the recursive helper function to store the Topological Sort starting from the source node
#     topological_sort_util(start, visited, stack, graph)

#     return stack


# def parse_component(component):
#     pattern = r'n1\s*=\s*(\d+)\s+n2\s*=\s*(\d+)\s+(R|L|C)\s*=\s*([0-9.e+-]+)'
#     match = re.match(pattern, component.strip())
#     if match:
#         return match.groups()
#     else:
#         return None

# def compute_abcd_matrix(frequency, component):
#     pattern = r'n1\s*=\s*(\d+)\s+n2\s*=\s*(\d+)\s+(R|L|C)\s*=\s*([0-9.e+-]+)'
#     match = re.match(pattern, component.strip())
#     if not match:
#         print(f"Component format error or unmatched component: '{component}'")
#         return None

#     node1, node2, type, value = match.groups()
#     value = float(value)

#     omega = 2 * np.pi * frequency
#     if type == 'R':
#         return np.array([[1, value], [0, 1]], dtype=complex)
#     elif type == 'L':
#         return np.array([[1, complex(0, omega * value)], [0, 1]], dtype=complex)
#     elif type == 'C':
#         return np.array([[1, 0], [complex(0, -1 / (omega * value)), 1]], dtype=complex)

#     return None

# def cascade_matrices(matrices):
#     result = np.identity(2, dtype=complex)  # Ensure it's a complex type to handle inductors and capacitors
#     for matrix in matrices:
#         if matrix is not None:
#             result = np.dot(result, matrix)
#         else:
#             print("Invalid matrix skipped")
#     return result

# def calculate_output_variables(abcd_matrix, vt, rs, rl):
#     # a, b, c, d = abcd_matrix.flatten()
#     # zl = complex(rl)
#     # zs = complex(rs)

#     # av = 1 / (a + b / zl)
#     # ai = 1 / (c * zl + d)
#     # av_conj = np.conj(av)
#     # ap = av * av_conj

#     # zin = (a * zl + b) / (c * zl + d)
#     # zout = (d * zs + b) / (c * zs + a)

#     # vin = vt / (zin + zs)
#     # iin = vin / zs
#     # vout = av * vin
#     # iout = ai * iin

#     # pin = vin * np.conj(iin)
#     # pout = vout * np.conj(iout)
    
#     # Calculate the overall input and output impedances using the total cascaded ABCD matrix
#     a, b, c, d = abcd_matrix.flatten()
#     zin = (a * rl + b) / (c * rl + d)
#     zout = (d * rs + b) / (c * rs + a)

#     # Calculate the voltage and current gains using the total cascaded ABCD matrix
#     av = 1 / (a + b / rl)
#     ai = 1 / (c * rl + d)

#     # Calculate other parameters
#     vin = vt / (zin + rs)
#     iin = vin / zin
#     vout = vin * av
#     iout = iin * ai
#     pin = abs(vin) ** 2 / rs.real
#     pout = abs(vout) ** 2 / rl.real

#     return {
#         'Vin': vin, 'Vout': vout, 'Iin': iin, 'Iout': iout,
#         'Pin': pin, 'Zin': zin, 'Pout': pout, 'Zout': zout,
#         'Av': av, 'Ai': ai,
#     }

# def format_all_results(frequencies, output_structure):
#     formatted_results = []
#     for i, f in enumerate(frequencies):
#         result = {'Freq': f"{f:.3e}"}
#         for key in output_structure:
#             if key not in ['Freq']:  
#                 result[f'Re({key})'] = f"{output_structure[key][i].real:.3e}"
#                 result[f'Im({key})'] = f"{output_structure[key][i].imag:.3e}"
#         formatted_results.append(result)
#     return formatted_results

# def write_output_file(filename, output_data, all_results):
#     with open(filename, 'w', newline='') as csvfile:
#         fieldnames = ['Freq']
#         for name, unit in output_data:
#             if unit != 'L':  
#                 fieldnames.extend([f'Re({name})', f'Im({name})'])
#             else:  
#                 fieldnames.append(f'Re({name})')
#                 fieldnames.append(f'Im({name})')

#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()
#         units_row = {'Freq': 'Hz'}
#         for name, unit in output_data:
#             if unit != 'L':
#                 units_row[f'Re({name})'] = unit
#                 units_row[f'Im({name})'] = unit
#             else:
#                 units_row[f'Re({name})'] = 'L'
#                 units_row[f'Im({name})'] = 'L'
#         writer.writerow(units_row)
#         for result in all_results:
#             writer.writerow(result)
            
# def main(input_file, output_file):
#     # Parse the circuit file
#     circuit_data, terms_data, output_data = parse_net_file(input_file)

#     # Find the maximum node number which will be our load node
#     parsed_components = (parse_component(comp) for comp in circuit_data)
#     valid_components = [comp for comp in parsed_components if comp is not None]
#     max_node = max(int(n) for n, _, _, _ in valid_components)
#     load_node = str(max_node)

#     # Build the circuit graph
#     graph = build_circuit_graph(circuit_data)

#     # Perform a topological sort starting from the source node (0)
#     sorted_nodes = topological_sort(graph, '0')
    
#     # Map node pairs to components
#     node_to_component = {f"{n1}-{n2}": c for n1, n2, _, _ in valid_components for c in circuit_data if f"n1={n1} n2={n2}" in c or f"n1={n2} n2={n1}" in c}
    
#     # Create a list of components in the order of sorted nodes
#     sorted_components = [node_to_component[f"{sorted_nodes[i]}-{sorted_nodes[i+1]}"] for i in range(len(sorted_nodes) - 1)]

#     if 'LFstart' in terms_data and 'LFend' in terms_data:
#             # Logarithmic sweep
#             f_start = terms_data['LFstart']
#             f_end = terms_data['LFend']
#             frequencies = np.logspace(np.log10(f_start), np.log10(f_end), num=terms_data['Nfreqs'])
#     else:
#         # Linear or default frequency sweep
#         f_start = terms_data.get('Fstart', 1)  # Default start frequency if not specified
#         f_end = terms_data.get('Fend', 1e6)    # Default end frequency if not specified
#         frequencies = np.linspace(f_start, f_end, num=terms_data.get('Nfreqs', 10))

#     # Output structure preparation
#     output_structure = {name: [] for name, _ in output_data}

#     # Perform calculations for each frequency
#     for f in frequencies:
#         matrices = [compute_abcd_matrix(f, component) for component in sorted_components]
#         total_matrix = cascade_matrices(matrices)

#         # Calculate all output variables for this frequency
#         results = calculate_output_variables(total_matrix, terms_data['VT'], terms_data.get('RS', Z_SOURCE), terms_data.get('ZL', Z_SOURCE))

#         # Store the results in the output structure
#         for key in results:
#             output_structure[key].append(results[key])

#     # Format and write the results to the output file
#     all_results = format_all_results(frequencies, output_structure)
#     write_output_file(output_file, output_data, all_results)

# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python main.py input_file output_file")
#         sys.exit(1)
#     main(sys.argv[1], sys.argv[2])