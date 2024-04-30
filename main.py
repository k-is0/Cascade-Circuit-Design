import sys
import numpy as np

from impedance_init import impedance_matrix
from parse_net_file import parse_net_file
from cascade_matrices import cascade_matrices
from csv_writer import write_csv_data_row, write_csv_header, write_empty_output_file
from calculate_output_variables import calculate_output_variables
from parse_component import parse_component

input_file, output_file = None, None
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
        parsed_components = [parse_component(line, output_file) for line in circuit_data]
        sorted_components = sorted(parsed_components, key=lambda x: x[0])
    except ValueError as e:
        print(e)  # If there is a format error in the components
        sys.exit(1)  # Exit the program or handle it as needed
    
    if 'LFstart' in terms_data and 'LFend' in terms_data:
            # Logarithmic sweep
            f_start = terms_data['LFstart']
            f_end = terms_data['LFend']
            frequencies = np.logspace(np.log10(f_start), np.log10(f_end), num=terms_data['Nfreqs'])
    elif 'Fstart' in terms_data and 'Fend' in terms_data:
        # Linear or default frequency sweep
        f_start = terms_data.get('Fstart', 1)  # Default start frequency if not specified
        f_end = terms_data.get('Fend', 1e6)    # Default end frequency if not specified
        frequencies = np.linspace(f_start, f_end, num=terms_data.get('Nfreqs', 10))
    else: 
        print("Error: Frequency sweep not specified correctly in terms data.")
        write_empty_output_file(output_file)
        
    # # Output structure preparation
    # output_structure = {name: [] for name, _ in output_data}
        
    with open(output_file, 'w') as csvfile:
        write_csv_header(csvfile, output_data)
        
        for f in frequencies:
            abcd_matrices = []
            for n1, n2, component_type, value in sorted_components:
                matrix = impedance_matrix(f, n1, n2, component_type, value)
                abcd_matrices.append(matrix)
        
            total_matrix = cascade_matrices(abcd_matrices)
            
            # Calculate all output variables for this frequency
            results = calculate_output_variables(total_matrix, vt, rs, terms_data.get('RL', 50), output_data) 
                
            write_csv_data_row(csvfile, f, output_data, results)

    # # Format and write the results to the output file
    # all_results = format_all_results(frequencies, output_structure)
    
    # write_output_file(output_file, output_data, all_results)

if __name__ == "__main__":
    try:
        args = sys.argv[1:]
        if len(args) != 2:
            raise ValueError("Please provide input and output file paths.")
        input_file, output_file = args
        # Make sure input file is .net and output file is .csv
        if not input_file.endswith('.net') or not output_file.endswith('.csv'):
            raise ValueError("Input file must be a .net file and output file must be a .csv file.")
        main(input_file, output_file)
    except Exception as e:
        if output_file:
            write_empty_output_file(output_file)
        print(e)
        sys.exit(1)