import numpy as np

def impedance_matrix(frequency, n1, n2, component_type, value):
    # Convert n1 and n2 to integers to handle node connections properly
    n1, n2 = int(n1), int(n2)
    
    # Calculate the impedance or admittance based on component type
    if component_type == 'R':
        impedance = value
    elif component_type == 'L':
        impedance = 2j * np.pi * frequency * value
    elif component_type == 'C':
        impedance = -1j / (2 * np.pi * frequency * value)
    elif component_type == 'G':
        admittance = value
        impedance = 1 / admittance  # Convert conductance to resistance for series calculation
    else:
        raise ValueError(f"Invalid component type: {component_type}")
    
    # Determine if the component is a shunt (connected to ground)
    if n2 == 0:
        if component_type == 'G':  # Handling for shunt conductance
            return np.array([[1, 0], [impedance, 1]], dtype=complex)
        else:  # For R, L, C shunt components
            return np.array([[1, 0], [1/impedance, 1]], dtype=complex)
    else:
        # Handle components between any two nodes, including series conductance
        return np.array([[1, impedance], [0, 1]], dtype=complex)

# import numpy as np

# def impedance_matrix(frequency, n1, n2, component_type, value):
#     if component_type == 'R':
#         impedance = value
#     elif component_type == 'L':
#         impedance = 2j * np.pi * frequency * value
#     elif component_type == 'C':
#         impedance = (1/(2j * np.pi * frequency * value))
#     elif component_type == 'G':
#         impedance = 1/value
#     else:
#         raise ValueError(f"Invalid component type: {component_type}")
    
#     # Shunt component connected to ground
#     if n2 == 0:
#         if component_type == 'G':  # Shunt conductance is a special case
#             return np.array([[1, 0], [1/impedance, 1]])
#         else:
#             return np.array([[1, 0], [1/impedance, 1]])

#     # Series component between two consecutive nodes
#     elif n2 == n1 + 1:
#         if component_type == 'G':
#             return np.array([[1, impedance], [0, 1]])
#         return np.array([[1, impedance], [0, 1]])
#     else:
#         raise ValueError(f"Invalid component connection: {n1} to {n2}")