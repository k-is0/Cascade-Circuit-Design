import re

def parse_component(component):
    pattern = r'n1\s*=\s*(\d+)\s+n2\s*=\s*(\d+)\s+(R|L|C|G)\s*=\s*([0-9.e+-]+)'
    match = re.match(pattern, component.strip())
    if not match:
        raise ValueError(f"Component format error: '{component}'")
    n1, n2, ctype, value = int(match.group(1)), int(match.group(2)), match.group(3), float(match.group(4))
    return n1, n2, ctype, value
