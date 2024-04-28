def format_all_results(frequencies, output_structure):
    formatted_results = []
    for i, f in enumerate(frequencies):
        result = {'Freq': f"{f:.3e}"}
        for key in output_structure:
            if i < len(output_structure[key]):
                result[f'Re({key})'] = f"{output_structure[key][i].real:.3e}"
                if key not in ['Freq']:  
                    result[f'Im({key})'] = f"{output_structure[key][i].imag:.3e}"
        formatted_results.append(result)
    return formatted_results