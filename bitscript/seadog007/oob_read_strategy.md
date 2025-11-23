# OOB Read Strategy for libc Address Leak

## The Problem

We need the `system` address to write to GOT, but:
- `system` is not in the binary (not imported)
- `system` is in libc
- We need to leak a libc address first

## Solution: OOB Read to Leak libc Address

**Strategy:**
1. Use bitmap overflow for **OOB read** (not just write!)
2. Read from `printf@GOT` (0x409048) - this contains libc's printf address
3. Calculate libc base: `libc_base = printf_got_value - printf_offset`
4. Calculate system: `system_addr = libc_base + system_offset`
5. Write system address to GOT
6. Trigger: `print("/bin/sh")` → `system("/bin/sh")`

## Using bitmap_get for OOB Read

**bitmap_get function:**
- Similar to `bitmap_set`, but reads instead of writes
- Can read from arbitrary addresses using same overflow
- Formula: `bitmap_data_ptr + (y * INT64_MAX + x) / 8`

**To read from `printf@GOT` (0x409048):**
```bitscript
# Calculate y value to hit GOT
# y = (0x409048 - bitmap_data_ptr) * 8 / INT64_MAX

# Read the value
int leaked = get(b1, x, calculated_y);
# This reads the QWORD at printf@GOT (libc's printf address)
```

## Challenge: Reading Full QWORD

**Problem:** `get()` only reads 1 bit, not full QWORD

**Solution:** Read 64 bits (one bit at a time) and reconstruct:
```bitscript
# Read 64 bits from GOT entry
# Reconstruct the QWORD value
# This gives us libc's printf address
```

## Alternative: Use Different Vulnerability

If bitmap_get doesn't work well, we could:
1. Use string overflow to corrupt a variable
2. Point variable's value_ptr to printf@GOT
3. Read the variable → leaks libc address
4. This might be easier than bit-by-bit read

## Next Steps

1. **Test OOB read with bitmap_get**
2. **Read from printf@GOT** to leak libc address
3. **Calculate system address** from libc base
4. **Write system to GOT** using bitmap_set
5. **Trigger shell** with print("/bin/sh")

