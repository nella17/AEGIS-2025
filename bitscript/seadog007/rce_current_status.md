# RCE Exploit - Current Status

## ✅ Completed

1. **Libc Offsets** - Got printf (0x60100) and system (0x58750) offsets
2. **Heap Leak** - Can leak heap addresses (targetaddr = 324521456)
3. **Address Calculation** - Calculated candidate addresses
4. **Bit-by-Bit Write Helper** - Python script to generate write code

## ⏳ Current Blocker

**Coordinate Calculation Issue:**

The bitmap overflow uses:
```
bit_index = y * INT64_MAX + x
byte_index = bit_index / 8
target_addr = bitmap_data_ptr + byte_index
```

**Problem:**
- We want to write to `value_ptr_addr` (offset ~7464 bytes from bitmap)
- `bit_offset = 7464 * 8 = 59712`
- But `y = 59712 / INT64_MAX = 0` (too small!)
- And `x = 59712 % 8 = 0`
- This writes to `bitmap_data_ptr + 0`, not to `value_ptr_addr`!

**The Issue:**
The bitmap overflow is designed for writing to addresses VERY far from the bitmap buffer (using the huge INT64_MAX multiplier). For nearby addresses (within a few KB), the calculation doesn't work as expected.

## Solutions

### Option 1: Use Negative Coordinates
If the bitmap buffer is AFTER the target address, we might need negative coordinates or a different approach.

### Option 2: Use Different Primitive
- **Use-After-Free** to directly corrupt variable entries
- **Double Free** for heap corruption
- **OOB Read** to find exact addresses first

### Option 3: Find Bitmap Buffer Location
We need to know where the bitmap buffer actually is. Options:
- Use OOB read to scan for bitmap data
- Use heap leak to find bitmap struct address
- Use GDB to inspect heap layout

### Option 4: Adjust Calculation
Maybe the bitmap buffer is at a different location than estimated. Try:
- Bitmap buffer much further away (so offset is larger)
- Or bitmap buffer before variables (negative offset handling)

## Recommended Next Steps

1. **Find Exact Bitmap Buffer Address**
   - Use OOB read to scan heap
   - Or leak bitmap struct address
   - Or use GDB to inspect

2. **Test with Known Address**
   - Once we know bitmap buffer address
   - Calculate correct coordinates
   - Test write to verify

3. **Alternative: Use Use-After-Free**
   - Self-assignment creates use-after-free
   - Can potentially read/write variable table directly
   - Might be easier than bitmap overflow

## Current Address Estimates

Based on `targetaddr = 324521456` (0x1355F5F0):

- **Entry address:** `targetaddr - 0x300 = 324520688` (0x1357CAF0)
- **Value pointer:** `entry_addr + 0x28 = 324520728` (0x1357CB18)
- **Bitmap buffer (estimated):** `targetaddr - 0x2000 = 324513264` (0x1357ADF0)

**Offset:** `value_ptr - bitmap_data = 7464 bytes`

**Problem:** This offset is too small for the INT64_MAX multiplier to work correctly.

## Next Action

**Try to find the actual bitmap buffer address using OOB read or heap inspection!**

Or try the use-after-free approach to directly corrupt variable entries.

