# RCE Payload Analysis - Two Crash Cases

## Crash Cases Identified

### Crash Case 1: `bitmap_size_of_crash.bs`
```bitscript
bitmap b1 = create(9223372036854775807, 2);
set(b1, 0, 1, 1);
int val = get(b1, 0, 1);
```

**Vulnerability:** Bitmap create signed integer overflow
- `create(9223372036854775807, 2)` bypasses bounds check
- `INT64_MAX * 2` overflows to `-2` (signed)
- Check `-2 > 0x800000` = FALSE → passes incorrectly
- Allocates tiny buffer (`malloc(0)`) but `width = INT64_MAX`
- `set(b1, 0, 1, 1)` calculates: `offset = (1 * INT64_MAX + 0) / 8`
- **Result:** Out-of-bounds write to arbitrary memory

**Exploitation Value:** ⭐⭐⭐⭐⭐
- **Arbitrary write primitive**
- Can target GOT directly
- Precise control over write address

### Crash Case 2: `strcat_crash.bs`
```bitscript
# Build large strings via repeated concatenation
string s1 = "A";
# ... 30+ doublings ...
string s2 = "B";
# ... 30+ doublings ...
string result = s1 + s2;  # Triggers overflow
```

**Vulnerability:** String concatenation integer overflow
- Repeated concatenation builds huge strings
- `len1 + len2` overflows to small value
- `malloc(small_value)` allocates tiny buffer
- `strcpy/strcat` write past end → heap overflow

**Exploitation Value:** ⭐⭐⭐
- Heap corruption confirmed
- Less precise than bitmap overflow
- Good for heap grooming

## Combined Exploit Strategy

### Primary Path: Bitmap Overflow → GOT Overwrite

**Advantages:**
1. **Direct arbitrary write** - no heap grooming needed
2. **Precise targeting** - can calculate exact offset to GOT
3. **Reliable** - works if we know heap address

**Challenges:**
1. **Bit-level writes** - `set()` only writes individual bits
   - Need 64 calls to write full QWORD (8 bytes)
   - Or find alternative write method
2. **Heap address** - need to know `bitmap_data_ptr`
   - Use GDB to find at runtime
   - Or calculate relative offsets
3. **system address** - still need system/execve
   - Check if in binary
   - Or use libc base + offset

### Secondary Path: String Overflow → Heap Grooming

**Use for:**
1. **Heap shaping** - arrange heap layout
2. **Corrupt structures** - variable entries, AST nodes
3. **Aid bitmap exploit** - position bitmap near target

## RCE Payload Structure

### Step 1: Setup
- Create "/bin/sh" string
- Initialize heap state

### Step 2: Bitmap Overflow
- `create(9223372036854775807, 2)` - bypass bounds check
- Calculate y value to hit `printf@GOT` (0x409048)

### Step 3: Write system Address
- Use `set()` to write bits of system address
- Or use heap corruption for byte-level write

### Step 4: Trigger
- `print("/bin/sh")` → `system("/bin/sh")` → **SHELL!**

## What We Still Need

1. **Heap address** - to calculate exact y value
2. **system address** - system@PLT or libc system
3. **Write method** - how to write full QWORD (not just bits)

## Next Steps

1. **Run payload** - confirm both crashes work together
2. **GDB analysis** - find heap address and bitmap_data_ptr
3. **Calculate offsets** - determine exact y value for GOT
4. **Craft final exploit** - combine all pieces for RCE

