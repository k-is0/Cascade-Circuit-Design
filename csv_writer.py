import csv

def write_csv_header(csvfile, output_data):
    headers = ['      Freq']
    units = ['        Hz']

    for header, unit in output_data:
        if not unit:
            unit = "L"  # Default unit if none provided

        # Handling different unit types with specific formatting
        if "dB" in unit:
            real_header = "{:>11}".format("|" + header + "|")
            imag_header = "{:>11}".format("/_" + header)
        else:
            real_header = "{:>11}".format("Re(" + header + ")")
            imag_header = "{:>11}".format("Im(" + header + ")")

        headers.append(real_header)
        headers.append(imag_header)
        units.append("{:>11}".format(unit))
        units.append("{:>11}".format(unit))

    # Convert lists to strings and join them with commas, ensuring no comma after the last entry
    header_line = ",".join(headers)
    unit_line = ",".join(units)

    # Write the formatted headers and units to the CSV file
    csvfile.write(header_line + "\n")
    csvfile.write(unit_line + "\n")

    # fieldnames = ['Freq']
    # for name, unit in output_data:
    #     if unit != 'L':  
    #         fieldnames.extend([f'Re({name})', f'Im({name})'])
    #     else:  
    #         fieldnames.append(f'Re({name})')
    #         fieldnames.append(f'Im({name})')

    # writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    # writer.writeheader()
    # units_row = {'Freq': 'Hz'}
    # for name, unit in output_data:
    #     if unit != 'L':
    #         units_row[f'Re({name})'] = unit
    #         units_row[f'Im({name})'] = unit
    #     else:
    #         units_row[f'Re({name})'] = 'L'
    #         units_row[f'Im({name})'] = 'L'
    # writer.writerow(units_row)

def write_csv_data_row(csvfile, f, output_data, results):
    # Write frequency directly with no extra padding but with a space before the value
    csvfile.write(" {:.3e},".format(f))

    # Initialize row for other data
    row = []
    for name, unit in output_data:
        value = results[name]
        data_real = "{:.3e}".format(value.real)
        data_imag = "{:.3e}".format(value.imag)
        # Append space before each value
        row.append(" {:>10}".format(data_real))
        row.append(" {:>10}".format(data_imag))
    row.append("")  # Add an empty field
    
    # Join the rest of the row with commas and write to file
    csvfile.write(",".join(row) + "\n")
    
    # row = [f'{f:.3e}']  # Frequency
    # for output in output_data:
    #     name = output[0]
    #     value = results[name]
    #     row.append(f'{value.real:.3e}')
    #     row.append(f'{value.imag:.3e}')
    # row.append('')  # Add an empty field
    # writer = csv.writer(csvfile)
    # writer.writerow(row)

def write_empty_output_file(output_file):
    with open(output_file, 'w') as csvfile:
        csvfile.close()