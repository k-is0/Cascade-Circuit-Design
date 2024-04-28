def format_all_results(frequencies, output_structure):
    formatted_results = []
    for i, f in enumerate(frequencies):
        result = {'Freq': f"{f:.3e}"}
        for key in output_structure:
            if key not in ['Freq']:  
                result[f'Re({key})'] = f"{output_structure[key][i].real:.3e}"
                result[f'Im({key})'] = f"{output_structure[key][i].imag:.3e}"
        formatted_results.append(result)
    return formatted_results