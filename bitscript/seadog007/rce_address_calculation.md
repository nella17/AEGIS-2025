# RCE Address Calculation Guide

## Your Leaked Addresses

From the output:
- `addr1 = 815392768` (0x309A0000)
- `addr2 = 815393072` (0x309A0130)
- `addr3 = 815393376` (0x309A0260)
- `targetaddr = 815393760` (0x309A03C0)

**Spacing:** ~304 bytes between strings (consistent)

## Step 4 Implementation

### Goal
Corrupt `target` variable's `value_ptr` to point to `printf@GOT` (0x409048)

### What We Need

1. **Variable Entry Address** (`entry_addr`)
   - Variable entry is 64 bytes (0x40)
   - Typically 0x200-0x400 bytes before string address
   - `entry_addr ≈ targetaddr - 0x300`

2. **value_ptr Address** (`value_ptr_addr`)
   - `value_ptr` is at offset 0x28 from entry start
   - `value_ptr_addr = entry_addr + 0x28`

3. **Bitmap Buffer Address** (`bitmap_data_ptr`)
   - Bitmap is allocated after variables
   - `bitmap_data_ptr ≈ targetaddr + 0x1000` (estimate)

4. **Calculate y and x**
   ```
   offset = value_ptr_addr - bitmap_data_ptr
   y = (offset * 8) / INT64_MAX
   x = (offset * 8) % 8
   ```

### The Challenge

**Problem:** We don't know exact addresses!

**Solution Options:**

1. **OOB Read to Find Addresses**
   - Use bitmap to scan heap backwards from `targetaddr`
   - Look for "target" name pattern (at offset 0x00 of variable entry)
   - When found, that's `entry_addr`

2. **Try Common Offsets**
   - Try: `targetaddr - 0x100`, `-0x200`, `-0x300`, `-0x400`
   - Write test values and check if `target` changes
   - If it changes, we found the right offset!

3. **Use Heap Grooming**
   - Control allocation order
   - Calculate based on known heap behavior

### Practical Approach

**Since we have leaked addresses, let's try:**

1. **Estimate entry_addr:**
   ```
   entry_addr = targetaddr - 0x300 = 815393760 - 0x300 = 815393216
   value_ptr_addr = entry_addr + 0x28 = 815393216 + 0x28 = 815393304
   ```

2. **Estimate bitmap_data_ptr:**
   ```
   bitmap_data_ptr = targetaddr + 0x1000 = 815393760 + 0x1000 = 815394760
   ```

3. **Calculate offset:**
   ```
   offset = value_ptr_addr - bitmap_data_ptr
   offset = 815393304 - 815394760 = -1456 (negative!)
   ```

**Problem:** Negative offset means `value_ptr` is BEFORE `bitmap_data_ptr`, which won't work with `y=0`!

**Solution:** We need `y=1` or use negative arithmetic, OR the bitmap buffer is actually BEFORE the variable entry.

### Alternative: Bitmap Buffer Location

**Maybe bitmap is allocated BEFORE variables?**
- Try: `bitmap_data_ptr = targetaddr - 0x2000`
- Then offset would be positive

### Next Steps

1. **Create OOB read script** to find exact addresses
2. **Test different offsets** to find entry_addr
3. **Once found, calculate exact y and x**
4. **Write 0x409048 bit-by-bit**

The key is finding the exact addresses!

