# Alternative Approach: Use OOB Read to Find Exact Addresses

## Problem

The estimated addresses don't work. We got `440328224` instead of `1094795585`.

**What `440328224` is:**
- Hex: `0x1A3F5A20`
- This might be:
  - Another heap address
  - Part of a string structure
  - Part of variable entry
  - Random memory

## Solution: Find Exact Addresses via OOB Read

### Strategy 1: Scan for Variable Entry

**Variable entry structure:**
- Offset 0x00-0x1F: Variable name ("target")
- Offset 0x20: Type (1 = string)
- Offset 0x28: value_ptr (points to string struct)

**Approach:**
1. Use OOB read to scan heap backwards from `targetaddr`
2. Look for "target" string at offset 0x00
3. When found, that's the entry address
4. `value_ptr = entry_addr + 0x28`

### Strategy 2: Use Use-After-Free

**Approach:**
1. Create use-after-free with self-assignment
2. Groom heap to make corrupted variable point to variable table
3. Read variable entries directly
4. Find `target` entry and get its address

### Strategy 3: Try Different Bitmap Buffer Locations

**Maybe bitmap buffer is:**
- Much further away (larger offset)
- At a different relative position
- Allocated differently

**Try:**
- `bitmap_data_ptr = targetaddr - 0x4000`
- `bitmap_data_ptr = targetaddr - 0x8000`
- `bitmap_data_ptr = targetaddr + 0x1000` (after variables)

### Strategy 4: Brute Force

**Try all combinations:**
- Entry offsets: 0x100, 0x200, 0x300, 0x400, 0x500, 0x600
- Bitmap offsets: -0x1000, -0x2000, -0x3000, +0x1000, +0x2000

**Created:** `rce_brute_force_offsets.bs` to test all combinations

## Recommended Next Action

**Run the brute force script** to find which offset combination works!

Or use OOB read to find exact addresses more reliably.

