import csv

def write_output_file(filename, output_data, all_results):
    with open(filename, 'w', newline='') as csvfile:
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
        for result in all_results:
            writer.writerow(result)