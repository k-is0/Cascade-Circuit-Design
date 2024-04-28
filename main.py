import sys
import numpy as np

from impedance_init import impedance_init
from parse_net_file import parse_net_file
from cascade_matrices import cascade_matrices
from write_output_file import write_output_file
from calculate_output_variables import calculate_output_variables
from format_all_results import format_all_results

# Constants
Z_SOURCE = 50  # Assuming the source impedanceedance Rs is 50 Ohms if not specified in the file

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
    matrices = []
    for f in frequencies:
        matrices.append(impedance_init(f, component) for component in circuit_data)
        # replace the for loop with list comprehension in impedance_init.py
        
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