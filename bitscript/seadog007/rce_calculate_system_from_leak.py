#!/usr/bin/env python3
"""
Calculate system() address from leaked libc address
"""

def calculate_system_addr(leaked_addr, leaked_function="setvbuf"):
    """Calculate system() address from leaked function address"""
    
    # Known offsets (from earlier readelf output)
    printf_offset = 0x60100
    system_offset = 0x58750
    
    # If leaked function is setvbuf, need its offset
    # For now, assume we can get it
    # Or use printf if we leak printf instead
    
    print(f"Leaked address: 0x{leaked_addr:x} ({leaked_addr})")
    print(f"Assuming this is {leaked_function}")
    print()
    
    # We need the offset of the leaked function
    # For setvbuf, would need: readelf -s libc.so.6 | grep setvbuf
    print("To calculate system address:")
    print(f"  1. Get {leaked_function} offset from libc")
    print(f"  2. libc_base = leaked_addr - {leaked_function}_offset")
    print(f"  3. system_addr = libc_base + 0x58750")
    print()
    
    # Example calculation (if we had setvbuf offset)
    # setvbuf_offset = 0xXXXXX  # Need to get this
    # libc_base = leaked_addr - setvbuf_offset
    # system_addr = libc_base + 0x58750
    
    return None  # Can't calculate without setvbuf offset

def main():
    leaked_addr = 0x7ca596e88550  # From user output
    
    print("=== Calculate system() Address ===")
    print()
    
    # Try to calculate
    result = calculate_system_addr(leaked_addr)
    
    print("To complete the calculation:")
    print("  1. Run: readelf -s libc.so.6 | grep setvbuf")
    print("  2. Get setvbuf offset")
    print("  3. Calculate libc_base and system_addr")
    print()
    print("Or leak printf address instead (we already have its offset)")

if __name__ == "__main__":
    main()

