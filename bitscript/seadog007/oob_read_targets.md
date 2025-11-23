# OOB Read Targets - Where to Read From

## Primary Targets for Information Leak

### 1. GOT Entries (Most Important)
**Why:** Contain libc addresses we need for RCE

**Targets:**
- `printf@GOT`: **0x409048** - Contains libc's printf address
- `puts@GOT`: **0x409038** - Contains libc's puts address  
- `free@GOT`: **0x409018** - Contains libc's free address
- `fprintf@GOT`: **0x409078** - Contains libc's fprintf address

**What we get:**
- Leak any GOT entry → get libc address
- Calculate libc base: `libc_base = leaked_addr - function_offset`
- Calculate system: `system_addr = libc_base + system_offset`

### 2. Variable Table Entries
**Why:** Contain pointers to heap-allocated data

**Structure (0x40 bytes per entry):**
- Offset 0x00-0x1F: `name[32]` (variable name)
- Offset 0x20: `type` (0=int, 1=string, 2=bitmap)
- Offset 0x28: `value_ptr` (8 bytes) - **TARGET!**

**What we get:**
- If we read a variable's `value_ptr`, we get heap address
- Can use this to calculate offsets for GOT reads
- Or read from the pointed-to location

### 3. Heap Metadata
**Why:** Can reveal heap layout and addresses

**What to look for:**
- Chunk headers (size, flags, prev_size)
- Free list pointers (fd/bk pointers)
- Heap base address

**Where:**
- Adjacent to our tiny buffer (y=0, different x values)
- Before/after allocations

### 4. Stack Addresses
**Why:** Could reveal return addresses or stack layout

**Challenge:** Stack is usually far from heap, hard to reach

### 5. Binary Code/Data Sections
**Why:** Could reveal binary base or code addresses

**Targets:**
- `.text` section (code)
- `.data` section (initialized data)
- `.bss` section (uninitialized data)

## Reading Strategy

### Step 1: Safe Reads (y=0)
- Read from within buffer
- Read adjacent bytes (different x values)
- Look for heap metadata or pointers

### Step 2: Calculate Heap Address
- If we find heap metadata, extract heap base
- Or use variable table entries to find heap addresses

### Step 3: Calculate y for GOT
- Once we have heap address (`bitmap_data_ptr`):
  ```
  y = (0x409048 - bitmap_data_ptr) * 8 / INT64_MAX
  ```

### Step 4: Read from GOT
- Use calculated y value
- Read 64 bits (bits 0-63) to reconstruct QWORD
- This gives us libc address

### Step 5: Calculate system
- `libc_base = leaked_printf - printf_offset`
- `system_addr = libc_base + system_offset`

## Practical Approach

**Since we don't know heap address:**
1. **Try variable corruption** - More reliable than direct GOT read
2. **Use string overflow** - Corrupt variable's value_ptr to point to GOT
3. **Read variable** - Gets libc address (byte-level, not bit-level!)

**Or:**
1. **Use GDB** - Find heap address at runtime
2. **Calculate exact y** - For direct GOT read
3. **Read 64 bits** - Reconstruct libc address

## Recommended: Variable Corruption Approach

**Why it's better:**
- No need to know heap address
- Byte-level read (full QWORD at once)
- More reliable
- Avoids segfault from huge offsets

**Steps:**
1. Heap groom with string overflow
2. Corrupt variable's value_ptr → printf@GOT
3. Read variable → leaks libc address
4. Calculate system
5. Write system to GOT
6. Trigger shell

