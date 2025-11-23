# Address Issue Analysis

## Observation

**Test result:** `test = 440328224` which equals `targetaddr`!

**This means:**
- We're reading the **string address**, not the corrupted `value_ptr`
- The write either:
  1. Didn't happen (wrong address)
  2. Happened to wrong location
  3. `value_ptr` wasn't actually corrupted

## Why This Happens

**When reading `int test = target;`:**
1. `get_variable("target")` returns variable entry
2. Reads `entry.value_ptr` (at offset 0x28)
3. If `value_ptr` points to string struct, reads string address
4. If `value_ptr` was corrupted, should read from corrupted address

**The fact we get `targetaddr` suggests:**
- `value_ptr` still points to the original string struct
- Our write didn't corrupt it (wrong address)
- Or we're reading from the wrong variable entry

## Solutions

### Option 1: Verify We're Writing to Correct Location

**Check:**
- Is `value_ptr_addr` calculation correct?
- Is `bitmap_data_ptr` estimate correct?
- Are we writing to the right offset?

**Test:** Write to a known address first (like another variable's value_ptr)

### Option 2: Try Different Offsets

**The bitmap buffer might be:**
- At a different location than estimated
- Allocated before variables (negative offset)
- Allocated after variables (positive offset, but larger)

**Try:**
- `bitmap_data_ptr = targetaddr - 0x1000` (smaller negative)
- `bitmap_data_ptr = targetaddr - 0x4000` (larger negative)
- `bitmap_data_ptr = targetaddr + 0x2000` (positive, but test)

### Option 3: Use OOB Read to Find Exact Addresses

**More reliable:**
1. Use OOB read to scan heap
2. Find variable entry by looking for "target" name
3. Find bitmap buffer by looking for bitmap struct
4. Use exact addresses

### Option 4: Use Use-After-Free Instead

**Avoid address finding:**
1. Use self-assignment for use-after-free
2. Groom heap to control allocations
3. Corrupt variable entries directly
4. No need for exact addresses!

## Recommended Action

**Try the brute force script** (`rce_brute_force_offsets.bs`) to test multiple offset combinations.

Or **pivot to use-after-free approach** which might be more reliable.

