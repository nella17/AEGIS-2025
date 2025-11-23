# Why Writes Aren't Working - Analysis

## Observation

All test writes return `targetaddr` instead of the test value `0x41414141`.

**This means:**
- We're reading the **string address** (targetaddr)
- The `value_ptr` was **not corrupted**
- Our writes are **not hitting the target address**

## Possible Reasons

### 1. Wrong Bitmap Buffer Address

**The bitmap buffer might be:**
- At a completely different location
- Not where we estimated
- Allocated in a different order

**Solution:** Find exact bitmap buffer address using OOB read

### 2. Wrong Entry Address

**The variable entry might be:**
- At a different offset from string
- Not at `targetaddr - 0x300`
- Need to try different offsets

**Solution:** Try different entry offsets: `-0x100`, `-0x200`, `-0x400`, `-0x500`

### 3. Write Calculation Error

**The coordinate calculation might be wrong:**
- `bit_index = offset * 8` might not be correct
- Or `x = bit_index, y = 0` might not work for all cases
- Need to verify the formula

**Solution:** Test with a known address first

### 4. Bounds Check Preventing Write

**The bitmap_set function has bounds checks:**
```c
if (a2 < 0 || a2 >= *a1 || a3 < 0 || a3 >= a1[1])
```

**If `x = 59712` and `width = INT64_MAX`:**
- `59712 >= INT64_MAX` = FALSE ✅ (passes)
- `0 >= 2` = FALSE ✅ (passes)

**So bounds check should pass...**

### 5. Write to Wrong Memory

**Maybe we're writing to:**
- A different variable's entry
- Heap metadata
- Unused memory
- But not to `target.value_ptr`

**Solution:** Verify by reading back from exact address

## Debugging Strategy

### Step 1: Verify Write Mechanism Works

**Test:** Write to a known safe location first
- Write to another variable's value_ptr
- Or write to a test address we can verify

### Step 2: Find Exact Addresses

**Use OOB read to:**
- Find variable entry by scanning for "target" name
- Find bitmap buffer by looking for our test pattern
- Use exact addresses instead of estimates

### Step 3: Try Use-After-Free

**Alternative approach:**
- Use self-assignment for use-after-free
- Groom heap to control allocations
- Corrupt variable entries directly
- Avoid bitmap overflow coordinate issues

## Recommended Next Action

**Try the use-after-free approach** - it might be more reliable than finding exact addresses!

Or **use OOB read to find exact bitmap buffer address** before trying to write.

