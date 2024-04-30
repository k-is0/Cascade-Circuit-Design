import re
from csv_writer import write_empty_output_file

def parse_component(component, output_file):
    # Parse the component line and return the node numbers, component type, and value
    pattern = r'n1\s*=\s*(\d+)\s+n2\s*=\s*(\d+)\s+(R|L|C|G)\s*=\s*([0-9.e+-]+)'
    match = re.match(pattern, component.strip())
    if not match:
        # If the component is not formatted correctly, write an empty output file and raise an error
        write_empty_output_file(output_file)
        raise ValueError(f"Error: Component '{component}' not formatted correctly.")
    n1, n2, ctype, value = int(match.group(1)), int(match.group(2)), match.group(3), float(match.group(4))
    return n1, n2, ctype, value

def parse_net_file(file_path):
    # Parse the input file and return the circuit data, terms data, and output data
    with open(file_path, 'r') as file:
        data = file.read().splitlines()

    circuit_data = []
    terms_data = {}
    output_data = []
    current_block = None

    for line in data:
        # Strip leading and trailing whitespace and ignore empty lines and comments
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # Check for block tags and set the current block
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
                # Split each pair into key and value and store them in the terms_data dictionary
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
            
            # If the output variable has no unit manually add 'L'
            if len(parts) == 1:
                output_data.append((parts[0], 'L')) 
            elif len(parts) == 2:
                output_data.append((parts[0], parts[1]))
            else:
                print(f"Warning: Unexpected output format in line: {line}") # Handle unexpected output format

    return circuit_data, terms_data, output_data

def parse_arguments(args):
    # Parse the command line arguments and return the input and output file paths
    if len(args) != 2:
        # If the number of arguments is not 2, raise an error
        raise ValueError("Please provide exactly two arguments: input file path and output file path.")
    input_file, output_file = args
    if not input_file.endswith('.net'):
        raise ValueError("Input file must be a .net file.") 
    if not output_file.endswith('.csv'):
        raise ValueError("Output file must be a .csv file.")
    return input_file, output_file