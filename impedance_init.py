import numpy as np
import re

def impedance_init(frequency, component):
    components = []
    
    pattern = r'n1\s*=\s*(\d+)\s+n2\s*=\s*(\d+)\s+(R|L|C|G)\s*=\s*([0-9.e+-]+)'
    match = re.match(pattern, component.strip())
    if not match:
        print(f"Component format error or unmatched component: '{component}'")
        return None
    
    components.append((int(match.group(1)), int(match.group(2)), match.group(3), float(match.group(4))))
    components.sort()
    
    matrix_list = []
    
    for element in components:
        if element[2] == 'R':
            impedance = element[3] 
        elif element[2] == 'L':
            impedance = 2j * np.pi * frequency * element[3]
        elif element[2] == 'C':
            impedance = 1/(2j * np.pi * frequency * element[3])
        elif element[2] == 'G':
            impedance = 1/element[3] 
        else:
            raise ValueError(f"Invalid component type: {element[2]}")
            
        if element[1] == 0:
            return np.array([[1, 0], [1/impedance, 1]])
        elif element[1] == element[0] + 1:
            matrix_list.append(np.array([[1, impedance], [0, 1]]))
        else:
            raise ValueError(f"Invalid component nodes: {element[0]}, {element[1]}")
        
    return matrix_list