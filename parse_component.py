import re
import sys
from csv_writer import write_empty_output_file

def parse_component(component, output_file):
    pattern = r'n1\s*=\s*(\d+)\s+n2\s*=\s*(\d+)\s+(R|L|C|G)\s*=\s*([0-9.e+-]+)'
    match = re.match(pattern, component.strip())
    if not match:
        write_empty_output_file(output_file)
        raise ValueError(f"Error: Component '{component}' not formatted correctly.")
    n1, n2, ctype, value = int(match.group(1)), int(match.group(2)), match.group(3), float(match.group(4))
    return n1, n2, ctype, value
