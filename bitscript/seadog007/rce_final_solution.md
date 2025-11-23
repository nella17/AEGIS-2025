# RCE Final Solution - The Real Problem

## The Issue

**Bitmap buffer is on heap (high address ~0x7f3851400000)**
**GOT is at low address (0x409048)**
**Offset is negative!**

We can't write from high heap address to low GOT address using `y=0` and positive `x`.

## Solutions

### Option 1: Find Bitmap Buffer Address

**Use OOB read to:**
- Scan heap for bitmap struct
- Read `data_ptr` field (offset 0x10)
- Calculate exact offset to GOT
- Use appropriate `y` value (might need y=1 or wrapping)

**Challenge:** Finding bitmap struct in heap is hard

### Option 2: Use Variable Corruption Chain

**Two-step write:**
1. Use bitmap overflow to corrupt variable entry's `value_ptr` to `printf@GOT`
2. Use variable assignment to write `system_addr` to GOT

**Still needs:** Variable entry address and bitmap buffer address

### Option 3: Use-After-Free Direct Write

**If we can:**
- Create UAF on variable entry
- Groom heap so freed entry is reused
- Corrupt `value_ptr` to `printf@GOT`
- Write `system_addr` through variable

**Challenge:** Hard to control heap layout precisely

### Option 4: Negative Offset / Wrapping

**If bitmap calculation allows:**
- Use negative `y` (unlikely)
- Or wrap the calculation (integer overflow)
- Might reach GOT from heap

**Unlikely to work** - bounds checks probably prevent this

## Recommended: Variable Corruption Chain

**Why it's best:**
1. We already have heap leak (type confusion)
2. Variable entries are predictable (0x40 bytes, before string data)
3. Can estimate variable entry address from heap leak
4. Two-step write is more reliable

**Steps:**
1. **Leak heap address** (already done)
2. **Estimate variable entry address** (`heapaddr - 0x300`)
3. **Estimate bitmap buffer** (`heapaddr + 0x1000` or try different offsets)
4. **Corrupt `value_ptr`** to `printf@GOT` using bitmap overflow
5. **Write `system_addr`** to GOT through corrupted variable
6. **Trigger shell**

## Next Action

**Create script that tries variable corruption chain with different bitmap buffer estimates!**

