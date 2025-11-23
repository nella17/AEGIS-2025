# Where to Read - OOB Read Targets

## Best Targets for Information Leak

### 1. **GOT Entries** (Highest Priority) ⭐⭐⭐⭐⭐

**Why:** Direct path to libc addresses

**Targets:**
- `printf@GOT`: **0x409048** - Contains libc's printf address
- `puts@GOT`: **0x409038** - Contains libc's puts address
- `free@GOT`: **0x409018** - Contains libc's free address

**What you get:**
- Leak any GOT entry → get libc function address
- Calculate libc base: `libc_base = leaked_addr - function_offset`
- Calculate system: `system_addr = libc_base + system_offset`

**Challenge:** Need heap address to calculate exact y value

### 2. **Variable Table Entries** ⭐⭐⭐⭐

**Why:** Contain pointers to heap data, can help find heap addresses

**Structure:**
- Each entry: 0x40 bytes
- Offset 0x28: `value_ptr` (8 bytes) - **This is what we want!**

**What you get:**
- Heap addresses (from value_ptr)
- Can use to calculate offsets for GOT reads
- Or read from pointed-to locations

**Where:** Variable table is on heap, need to find it

### 3. **Heap Metadata** ⭐⭐⭐

**Why:** Reveals heap layout and base address

**What to look for:**
- Chunk size fields
- Free list pointers (fd/bk)
- Heap base address

**Where:** Adjacent to allocations (y=0, different x values)

### 4. **String/Bitmap Data** ⭐⭐

**Why:** Might contain pointers or reveal heap layout

**What to look for:**
- String data (ASCII patterns)
- Bitmap structures
- Pointers within structures

## Reading Strategy

### Phase 1: Safe Exploration (y=0)
1. Read from buffer (y=0, x=0 to x=1024)
2. Look for non-zero bits
3. Identify patterns (pointers, metadata)

### Phase 2: Find Heap Address
1. Look for heap metadata in safe reads
2. Or find variable table entries
3. Extract heap base or variable addresses

### Phase 3: Calculate GOT Read
1. Once we have heap address:
   ```
   y = (0x409048 - bitmap_data_ptr) * 8 / INT64_MAX
   ```
2. Read 64 bits from GOT
3. Reconstruct libc address

### Phase 4: Get system Address
1. `libc_base = leaked_printf - printf_offset`
2. `system_addr = libc_base + system_offset`
3. Write system to GOT
4. Trigger shell

## Practical Recommendation

**Since direct GOT read is hard without heap address:**

**Use Variable Corruption Approach:**
1. Heap groom with string overflow
2. Corrupt variable's `value_ptr` → point to `printf@GOT`
3. Read variable → leaks libc address (byte-level!)
4. Calculate system
5. Write system to GOT
6. Trigger: `print("/bin/sh")` → shell

**This avoids:**
- Need to know heap address
- Bit-by-bit reading (64 calls)
- Segfault from huge offsets

## What the Scan Scripts Do

1. **oob_read_scan.bs**: Basic scan of safe locations
2. **oob_read_comprehensive.bs**: Systematic scan of many locations
3. Both look for non-zero bits that might indicate useful data

**Run them and look for:**
- Non-zero bits (especially in patterns of 8, 16, 32, 64)
- Patterns that look like addresses (high bits set)
- ASCII patterns (string data)

