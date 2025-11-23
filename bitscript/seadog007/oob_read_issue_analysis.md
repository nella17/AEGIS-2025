# OOB Read Issue Analysis

## Problem: Segfault on get(b1, 0, 1)

**Test:**
```bitscript
bitmap b1 = create(9223372036854775807, 2);
int leakedbit = get(b1, 0, 1);
```

**Result:** Segmentation fault

## Why It Segfaults

**Calculation:**
- `y = 1`, `x = 0`, `width = INT64_MAX`
- `offset = (1 * INT64_MAX + 0) / 8 = INT64_MAX / 8 = 0x0FFFFFFFFFFFFFFF`
- `read_addr = bitmap_data_ptr + 0x0FFFFFFFFFFFFFFF`
- This is a **huge offset**, way beyond valid memory → segfault

## The Challenge

**To read from `printf@GOT` (0x409048):**
```
bitmap_data_ptr + (y * INT64_MAX + x) / 8 = 0x409048
```

**Rearranging:**
```
y = (0x409048 - bitmap_data_ptr) * 8 / INT64_MAX
```

**Problem:** We don't know `bitmap_data_ptr` (heap address)

## Solutions

### Option 1: Safe Read (y=0)
- `y=0`: offset = 0 (reads from within buffer)
- Safe, but only reads from tiny buffer
- Might leak heap metadata or adjacent data
- Won't directly hit GOT

### Option 2: Variable Corruption Leak
- Use string overflow to corrupt variable entry
- Corrupt `value_ptr` to point to `printf@GOT`
- Read variable → leaks libc address
- **Advantage:** Byte-level read (not bit-level!)
- **Advantage:** Avoids segfault from huge offset

### Option 3: Find Heap Address First
- Use GDB to find `bitmap_data_ptr`
- Calculate exact y value
- Then read from GOT

### Option 4: Heap Grooming
- Use string overflow to position bitmap near GOT
- Then use smaller y value
- Requires precise heap layout control

### Option 5: Use Negative or Wrapped Values
- If calculation allows negative y
- Or if we can wrap the calculation
- Might give us a valid offset

## Recommended: Variable Corruption Approach

**Why it's better:**
1. **No segfault** - avoids huge offset issue
2. **Byte-level read** - reads full QWORD at once
3. **More reliable** - uses assignment which writes full values
4. **Easier to control** - corrupt pointer, then read

**Steps:**
1. Heap groom with string overflow
2. Use bitmap overflow to corrupt variable's `value_ptr`
3. Set `value_ptr = 0x409048` (printf@GOT)
4. Read variable → leaks libc printf address
5. Calculate system address
6. Write system to GOT (via variable corruption)
7. Trigger: `print("/bin/sh")` → shell

## Next Steps

1. **Test safe reads** (y=0) to see what we can leak
2. **Try variable corruption** approach
3. **Get heap address** from GDB
4. **Calculate exact y** for direct GOT read

The segfault confirms we need a different approach - variable corruption is likely the way to go!

