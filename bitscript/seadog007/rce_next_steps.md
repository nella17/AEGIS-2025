# RCE Next Steps - Action Plan

## Immediate Action Items

### 1. Get Libc Offsets ✅ DONE
```bash
readelf -s /lib/x86_64-linux-gnu/libc.so.6 | grep -E "printf|system"
```

**Result:**
- `printf` offset: `0x0060100`
- `system` offset: `0x0058750`

**Calculation:**
- `libc_base = leaked_printf_addr - 0x60100`
- `system_addr = libc_base + 0x58750`

**Status:** ✅ Complete - Saved in `libc_offsets.txt`

### 2. Create Address Finding Script (30 minutes)
**File:** `rce_find_exact_addresses.bs`

**Goal:** Find exact addresses of:
- Variable entry for a target variable
- Bitmap buffer address

**Approach:**
- Use heap leak to get starting point
- Use OOB read to scan heap for variable entries
- Or use calculation with refinement

### 3. Implement Bit-by-Bit Write (30 minutes)
**File:** `rce_write_address.bs`

**Goal:** Write a 64-bit address to arbitrary memory location

**Method:**
- Use bitmap overflow
- Calculate y and x coordinates
- Write each bit using `set()`

**Test:** Write test value to known address, verify it works

### 4. Corrupt Variable Entry (30 minutes)
**File:** `rce_corrupt_variable.bs`

**Goal:** Corrupt `target.value_ptr` to point to `printf@GOT` (0x409048)

**Steps:**
1. Find `target` variable entry address
2. Calculate `value_ptr_addr = entry_addr + 0x28`
3. Use bitmap overflow to write `0x409048` to `value_ptr_addr`
4. Verify corruption worked

### 5. Leak Libc Address (15 minutes)
**File:** `rce_leak_libc.bs`

**Goal:** Read `printf` address from GOT

**Steps:**
1. After corrupting `target.value_ptr` to `printf@GOT`
2. Read: `int libcprintf = target;`
3. Print the address
4. This is the libc address of `printf`

### 6. Calculate system() Address (10 minutes)
**File:** `rce_calculate_system.bs`

**Goal:** Calculate `system()` address

**Steps:**
1. Get libc offsets (from step 1)
2. `libc_base = libc_printf_addr - printf_offset`
3. `system_addr = libc_base + system_offset`
4. Print `system_addr`

### 7. Overwrite GOT (30 minutes)
**File:** `rce_overwrite_got.bs`

**Goal:** Write `system()` address to `printf@GOT`

**Steps:**
1. Use bitmap overflow to write `system_addr` to `0x409048`
2. Write bit-by-bit using calculated coordinates
3. Verify overwrite (optional)

### 8. Trigger RCE (5 minutes)
**File:** `rce_final.bs`

**Goal:** Get shell!

**Steps:**
1. Combine all previous steps
2. Execute: `print("/bin/sh");`
3. Should call `system("/bin/sh")` → SHELL!

## Recommended Order

**Start with these 3 in parallel:**

1. **Get libc offsets** (quick, needed for step 6)
2. **Create address finding script** (critical blocker)
3. **Implement bit-by-bit write** (needed for steps 4 and 7)

**Then proceed sequentially:**
4. Corrupt variable entry
5. Leak libc address
6. Calculate system address
7. Overwrite GOT
8. Trigger RCE

## Quick Win Strategy

**If address finding is hard, try this:**

1. **Use use-after-free** to read variable table entries directly
2. **Use heap grooming** to control allocation order
3. **Use OOB read** to scan heap systematically

## Testing Strategy

**For each step:**
1. Create test script
2. Run and verify it works
3. Check output/behavior
4. Refine if needed
5. Move to next step

## Estimated Time

- **Address finding:** 1-2 hours (biggest blocker)
- **Bit-by-bit write:** 30 minutes
- **Corrupt variable:** 30 minutes
- **Leak libc:** 15 minutes
- **Calculate system:** 10 minutes
- **Overwrite GOT:** 30 minutes
- **Trigger RCE:** 5 minutes

**Total:** ~3-4 hours to full RCE (if addresses are found)

## Current Status

✅ **Have:**
- Heap leak primitive
- Arbitrary write primitive (bitmap overflow)
- Use-after-free for heap grooming
- Known GOT address

⏳ **Need:**
- Exact variable entry address
- Exact bitmap buffer address
- Libc offsets
- Bit-by-bit write implementation

## Next Command to Run

```bash
# Get libc offsets
readelf -s /lib/x86_64-linux-gnu/libc.so.6 | grep -E "printf|system"
```

Then start working on address finding!

