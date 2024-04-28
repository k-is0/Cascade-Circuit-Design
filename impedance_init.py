import numpy as np
import re

def impedance_init(frequency, component):
    pattern = r'n1\s*=\s*(\d+)\s+n2\s*=\s*(\d+)\s+(R|L|C|G)\s*=\s*([0-9.e+-]+)'
    match = re.match(pattern, component.strip())
    if not match:
        print(f"Component format error or unmatched component: '{component}'")
        return None

    node1, node2, type, value = match.groups()
    value = float(value)
    
    # print(value)
    # print(node1, node2, type, value)

    if type == 'R':
        impedance = value 
    elif type == 'L':
        impedance = 2j * np.pi * frequency * value
    elif type == 'C':
        impedance = 1/(2j * np.pi * frequency * value)
    elif type == 'G':
        impedance = 1/value 
    else:
        raise ValueError(f"Invalid component type: {type}")
    
    # SORT IN ASCENDING N1, N2 ORDER
        
    if node2 == '0':
        return np.array([[1, 0], [1/impedance, 1]])
    elif int(node2) == int(node1) + 1:
        return np.array([[1, impedance], [0, 1]])
    else:
        raise ValueError(f"Invalid component nodes: {node1}, {node2}")