# Script Execution Order - Recommended Sequence

## Current Status
- ✅ Bitmap overflow confirmed (segfault on write)
- ✅ Safe reads work (y=0) but return all zeros
- ❌ Need to find useful data or use variable corruption

## Recommended Scripts to Run

### 1. **oob_read_comprehensive.bs** (First - Discovery)
**Purpose:** Systematically scan memory to find any non-zero data
**What it does:**
- Scans buffer (y=0) for 128 bits
- Scans adjacent memory (128-512 bits)
- Scans for variable table patterns
- Reads full bytes and QWORDs
- Looks for string data

**Why run this first:**
- Might find heap metadata or pointers
- Could reveal variable table locations
- Helps understand heap layout
- No segfault risk (all y=0 reads)

**Expected output:**
- List of bit positions with non-zero values
- Or all zeros (if nothing found)

### 2. **rce_leak_variable_corruption.bs** (Second - Exploit Attempt)
**Purpose:** Attempt variable corruption to leak libc address
**What it does:**
- Creates variable for corruption
- Heap grooms with string overflow
- Triggers string overflow
- Creates bitmap for corruption
- Tries to read leaked address

**Why run this:**
- Most promising path for libc leak
- Avoids bit-by-bit reading
- Uses byte-level read (full QWORD)

**Expected output:**
- Leaked libc address (if corruption works)
- Or 0/crash (if corruption didn't work)

### 3. **oob_read_scan.bs** (Alternative - Quick Test)
**Purpose:** Quick scan of safe locations
**What it does:**
- Reads first 8 bits
- Reads adjacent bytes
- Creates test variables

**Why run this:**
- Quick test
- Less comprehensive than comprehensive scan
- Good for quick checks

## Execution Order

**Step 1:** Run `oob_read_comprehensive.bs`
- See if we can find any useful data
- Look for patterns that might be pointers
- Check if variable table is accessible

**Step 2:** Based on results:
- **If found useful data:** Analyze and use for exploit
- **If all zeros:** Move to variable corruption approach

**Step 3:** Run `rce_leak_variable_corruption.bs`
- Attempt variable corruption leak
- See if we can get libc address

**Step 4:** If leak works:
- Calculate system address
- Write to GOT
- Trigger shell

## Quick Start

**Start with:**
```bash
python warpper.py oob_read_comprehensive.bs | ./bitscript
```

**Then try:**
```bash
python warpper.py rce_leak_variable_corruption.bs | ./bitscript
```

