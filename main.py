import sys
import numpy as np

from impedance_init import impedance_matrix
from parse_net_file import parse_net_file
from cascade_matrices import cascade_matrices
from write_output_file import write_output_file
from calculate_output_variables import calculate_output_variables
from format_all_results import format_all_results
from parse_component import parse_component

# Constants
Z_SOURCE = 50  # Assuming the source impedanceedance Rs is 50 Ohms if not specified in the file

def main(input_file, output_file):
    # Parse the circuit file
    circuit_data, terms_data, output_data = parse_net_file(input_file)
    
    # Handle source specification
    if 'VT' in terms_data:
        vt = terms_data['VT']
        rs = terms_data.get('RS', Z_SOURCE)  # Use default Z_SOURCE if RS is not specified
    elif 'IN' in terms_data:
        in_norton = terms_data['IN']
        rs = terms_data.get('RS', Z_SOURCE)  # Use default Z_SOURCE if RS is not specified
        vt = in_norton * rs  # Convert Norton source to Thevenin equivalent voltage
    else:
        print("Error: Source not specified correctly in terms data.")
        sys.exit(1)
    
    # Parse and sort components
    try:
        parsed_components = [parse_component(line) for line in circuit_data]
        sorted_components = sorted(parsed_components, key=lambda x: x[0])
    except ValueError as e:
        print(e)  # If there is a format error in the components
        sys.exit(1)  # Exit the program or handle it as needed

    
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
    
    abcd_matrices = []
    
    for f in frequencies:
        for n1, n2, component_type, value in sorted_components:
            matrix = impedance_matrix(f, n1, n2, component_type, value)
            abcd_matrices.append(matrix)
        
        total_matrix = cascade_matrices(abcd_matrices)
        
    print(abcd_matrices)
        
    # Calculate all output variables for this frequency
    results = calculate_output_variables(total_matrix, vt, rs, terms_data.get('ZL', 75))
    
    print(terms_data.get('ZL', 75), vt, rs)

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