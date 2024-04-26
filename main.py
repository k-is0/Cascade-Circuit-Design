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



# import numpy as np

# def parse_input(file_path):
#     with open(file_path, 'r') as file:
#         content = file.read()
    
#     blocks = {
#         'CIRCUIT': '',
#         'TERMS': '',
#         'OUTPUT': ''
#     }
    
#     for key in blocks.keys():
#         start_tag = f'<{key}>'
#         end_tag = f'</{key}>'
#         start_idx = content.find(start_tag) + len(start_tag)
#         end_idx = content.find(end_tag)
#         blocks[key] = content[start_idx:end_idx].strip()
        
#     return blocks

# # Example usage:
# blocks = parse_input('test.net')
# print(blocks['CIRCUIT'])  # This will print the content of the CIRCUIT block


# def get_abcd_matrix(component):
#     nodes, type_value = component.split(' ', 1)
#     n1, n2 = map(int, nodes[3:].split('=')[1], nodes[3:].split('=')[1])
#     if 'R=' in type_value:
#         R = float(type_value.split('=')[1])
#         return np.array([[1, R], [0, 1]])
#     elif 'L=' in type_value:
#         L = float(type_value.split('=')[1])
#         # Convert inductance to impedance at a given frequency if needed
#         # For DC, inductive impedance is zero
#         return np.array([[1, 0], [0, 1]])
#     elif 'C=' in type_value:
#         C = float(type_value.split('=')[1])
#         # Convert capacitance to admittance at a given frequency if needed
#         # For DC, capacitive impedance is infinite
#         return np.array([[1, 0], [0, 1]])
#     elif 'G=' in type_value:
#         G = float(type_value.split('=')[1])
#         return np.array([[1, 0], [G, 1]])
    
#     return np.eye(2)  # Identity matrix for an unrecognized component

# def calculate_total_abcd(circuit_block):
#     components = circuit_block.split('\n')
#     total_abcd = np.eye(2)
    
#     for component in components:
#         abcd = get_abcd_matrix(component)
#         total_abcd = np.dot(total_abcd, abcd)
    
#     return total_abcd


# def write_output(output_block, results, filename='results.csv'):
#     with open(filename, 'w') as file:
#         headers = output_block.split('\n')[0].split()
#         file.write(', '.join(headers) + '\n')
#         for result in results:
#             file.write(', '.join(map(str, result)) + '\n')

# # Example output block and results
# output_block = '<OUTPUT>\nVin V\nVout V\nIin A\nIout A\nPin W\nZout Ohms\nPout W\nZin Ohms\nAv\nAi\n</OUTPUT>'
# results = [[10, 5, 0.1, 0.05, 10, 50, 5, 25, 2, 0.5]]
# write_output(output_block, results)


# def main(input_file, output_file):
#     blocks = parse_input(input_file)
#     total_abcd = calculate_total_abcd(blocks['CIRCUIT'])
#     # Assuming you calculate results based on total_abcd and terms
#     results = []  # Populate with actual calculations
#     write_output(blocks['OUTPUT'], results, output_file)

# if __name__ == "__main__":
#     import sys
#     input_file = sys.argv[1]
#     output_file = sys.argv[2]
#     main(input_file, output_file)



"""
def parse_input_file(file_path):
    # Open the file and read the contents
    # Parse the CIRCUIT, TERMS, and OUTPUT sections
    # Return a dictionary or custom object with the parsed data

    return

def validate_data(data):
    # Check if all required vsections and entries are present
    # Ensure that all nodes referenced exist
    # Validate that the format of the values is correct (e.g., resistances are positive numbers)
    # Return True if data is valid or raise an exception with an error message if not
    return
    
class CircuitElement:
    def __init__(self, node1, node2, value, element_type):
        # Initialize a circuit element with nodes, value, and type (R, L, C, etc.)
        return
    
    def impedance(self, frequency):
        # Calculate and return the impedance of the element at the given frequency
        return

class Circuit:
    def __init__(self, elements):
        # Initialize with a list of CircuitElements
        return
    
    def analyse(self):
        # Perform the analysis using ABCD matrix method
        # Return the analysis results
        return

def export_results(data, output_file):
    # Format the results into the specified CSV format
    # Write the formatted data to the output_file
    return

def main(input_file, output_file):
    try:
        data = parse_input_file(input_file)
        validate_data(data)
        circuit = Circuit(data['elements'])
        results = circuit.analyse()
        export_results(results, output_file)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # This is where the program would actually start executing
    # Extract command line arguments for file names
    # Call the main function with the provided file paths
    pass

    
filepath = "/Users/kevin/Library/Mobile Documents/com~apple~CloudDocs/VSCode/EE20084/Cascade Circuit Design/a_Test_Circuit_1.net"
file = open(filepath, 'r')
lines = file.read()
print(lines)
file.close()
"""
