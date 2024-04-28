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