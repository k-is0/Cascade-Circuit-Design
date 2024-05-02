### Libraries ###
import sys
import numpy as np

### Local Modules ###
from csv_writer import *            
from matrix_calculations import *   
from net_parser import *

# global variables and constants
input_file, output_file = None, None
Z_SOURCE = 50      # Assuming the source impedanceedance Rs is 50 Ohms if not specified in the file

def main(input_file, output_file):
    circuit_data, terms_data, output_data = parse_net_file(input_file)
    
    # Handle source specs
    if 'VT' in terms_data:
        vt = terms_data['VT']
        rs = terms_data.get('RS', Z_SOURCE)     # Use default Z_SOURCE if RS is not specified
    elif 'IN' in terms_data:
        in_norton = terms_data['IN']
        rs = terms_data.get('RS', Z_SOURCE)     # Use default Z_SOURCE if RS is not specified
        vt = in_norton * rs                     # Convert Norton source to Thevenin equivalent voltage
    else:
        print("Error: Source not specified correctly in terms data.")
        sys.exit(1)
    
    # Parse and sort components
    try:
        parsed_components = [parse_component(line, output_file) for line in circuit_data]
        sorted_components = sorted(parsed_components, key=lambda x: x[0])
    except ValueError as e:
        print(e)        # If there is a format error in the components
        sys.exit(1)     # Exit the program or handle it as needed
    
    if 'LFstart' in terms_data and 'LFend' in terms_data:
            # Logarithmic sweep
            
            f_start = terms_data['LFstart']
            f_end = terms_data['LFend']
            frequencies = np.logspace(np.log10(f_start), np.log10(f_end), num=terms_data['Nfreqs'])
    elif 'Fstart' in terms_data and 'Fend' in terms_data:
        # Linear frequency sweep
        
        f_start = terms_data.get('Fstart', 1)       # Default start frequency if not specified
        f_end = terms_data.get('Fend', 1e6)         # Default end frequency if not specified
        frequencies = np.linspace(f_start, f_end, num=terms_data.get('Nfreqs', 10))
    else: 
        print("Error: Frequency sweep not specified correctly in terms data.")  # If frequency sweep is not specified
        write_empty_output_file(output_file) 
           
    # Write output data to the CSV file    
    with open(output_file, 'w') as csvfile:
        # Write headers and units to the CSV file
        write_csv_header(csvfile, output_data)
        
        # Calculate and write data for each frequency
        for f in frequencies:
            abcd_matrices = []  # Initialise list to store ABCD matrices for each component
            for n1, n2, component_type, value in sorted_components: 
                # Calculate the impedance matrix for each component
                matrix = impedance_matrix(f, n1, n2, component_type, value)
                abcd_matrices.append(matrix)    
        
            total_matrix = cascade_matrices(abcd_matrices) # Cascade all matrices to get the total matrix
            
            # Calculate all output variables for this frequency
            results = calculate_output_variables(total_matrix, vt, rs, terms_data.get('RL', 50)) 
            
            # Write the data row to the CSV file
            write_csv_data_row(csvfile, f, output_data, results)

if __name__ == "__main__":
    try:
        # Parse command line arguments
        input_file, output_file = parse_arguments(sys.argv[1:])
        main(input_file, output_file)
    except Exception as e:
        # Handle any exceptions and print error message
        print(f"Error: {e}")
        if output_file:
            write_empty_output_file(output_file)
        sys.exit(1)
