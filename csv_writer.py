import csv

def write_csv_header(csvfile, output_data):
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

def write_csv_data_row(csvfile, f, output_data, results):
    row = [f'{f:.3e}']  # Frequency
    for output in output_data:
        name = output[0]
        unit = output[1]
        value = results[name]
        row.append(f'{value.real:.3e}')
        row.append(f'{value.imag:.3e}')
    row.append('')  # Add an empty field
    writer = csv.writer(csvfile)
    writer.writerow(row)

def write_empty_output_file(output_file):
    with open(output_file, 'w') as csvfile:
        csvfile.close()