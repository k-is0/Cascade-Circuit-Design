import math

def write_csv_header(csvfile, output_data):
    headers = ['      Freq']
    units = ['        Hz']

    for header, unit in output_data:
        # Default unit
        if not unit:
            unit = "L"

        # Handling different unit types with specific formatting
        if "dB" in unit:
            if "Vout" in header or "Vin" in header:
                db_unit = "dBV"
            elif "Iout" in header or "Iin" in header:
                db_unit = "dBA"
            elif "Pout" in header or "Pin" in header:
                db_unit = "dBW"
            else:
                db_unit = "dB"
            
            # Splitting magnitude and phase into separate columns
            magnitude_header = "{:>11}".format("|" + header + "|")
            phase_header = "{:>11}".format("/_" + header)
            headers.extend([magnitude_header, phase_header])
            
            # dBV/dBA/dB and Rads as units for magnitude and phase respectively
            units.extend(["{:>11}".format(db_unit), "{:>11}".format("Rads")])
        else:
            # Splitting real and imaginary parts into separate columns
            real_header = "{:>11}".format("Re(" + header + ")")
            imag_header = "{:>11}".format("Im(" + header + ")")
            headers.extend([real_header, imag_header])
            units.extend(["{:>11}".format(unit), "{:>11}".format(unit)])

    # Convert lists to strings and join them with commas and no comma at the end
    header_line = ",".join(headers)
    unit_line = ",".join(units)

    # Write the formatted headers and units to CSV file
    csvfile.write(header_line + "\n")
    csvfile.write(unit_line + "\n")

def write_csv_data_row(csvfile, f, output_data, results):
    # Write frequency directly to file
    csvfile.write(" {:.3e},".format(f))

    # Initialise row for other data
    row = []
    for name, unit in output_data:
        # Get the value from the results dictionary
        if 'dB' in unit:
            value = results.get(name, 0)  # Get value if it exists
            magnitude = abs(value)  # Calculate magnitude of complex number
            db_value = 20 * math.log10(magnitude) if magnitude > 0 else 0  # Convert to dB
            data_db = "{:.3e}".format(db_value)
            # Append formatted dB value
            row.append(" {:>10}".format(data_db))
        else:
            value = results[name]
            data_real = "{:.3e}".format(value.real if hasattr(value, 'real') else value)
            data_imag = "{:.3e}".format(value.imag if hasattr(value, 'imag') else 0)
            # Append space before each value
            row.append(" {:>10}".format(data_real))
            row.append(" {:>10}".format(data_imag))

    # Add an empty field to ensure proper column alignment
    row.append("")

    # Join the rest of the row with commas and write to file
    csvfile.write(",".join(row) + "\n")

def write_empty_output_file(output_file):
    with open(output_file, 'w') as csvfile:
        csvfile.close()