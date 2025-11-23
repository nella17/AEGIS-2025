# CRITICAL: Bitmap Create Signed Integer Overflow - EXPLOITABLE!

## The Vulnerability Confirmed

**Test Result:**
```bitscript
bitmap b1 = create(9223372036854775807, 2);
```
**PASSED the bounds check!** ✅ This is the exploit!

## The Math

**Values:**
- `a1 = 9223372036854775807` = `INT64_MAX` = `0x7FFFFFFFFFFFFFFF`
- `a2 = 2`

**Bounds Check (Line 6):**
```c
if ( a1 <= 0 || a2 <= 0 || a2 * a1 > 0x800000 )
```

**The Overflow:**
- `a2 * a1 = 2 * INT64_MAX = 0xFFFFFFFFFFFFFFFE`
- In **signed 64-bit arithmetic**, this overflows and wraps to **-2** (negative!)
- Check: `-2 > 0x800000` = **FALSE** (negative is not > positive)
- **Check PASSES incorrectly!** ✅

## The Exploitation Path

**After check passes:**

1. **Line 19:** `v2 = a2 * a1 + 7`
   - `v2 = -2 + 7 = 5` (or wraps again, but likely 5)

2. **Line 20:** `if ( v2 < 0 )`
   - `5 < 0` = FALSE, so this branch doesn't execute

3. **Line 22:** `v4[2] = malloc((int)(v2 >> 3))`
   - `v2 >> 3 = 5 >> 3 = 0`
   - `malloc(0)` - **Allocates minimum chunk size!**

4. **Line 17-18:** Store width and height
   - `*v4 = 9223372036854775807` (width)
   - `v4[1] = 2` (height)

## The Exploit

**What happens:**
- Bitmap created with `width = INT64_MAX`, `height = 2`
- But data buffer is allocated with `malloc(0)` = **tiny buffer**
- When `set(b1, 0, 0, 1)` is called, it calculates:
  - `index = y * width + x = 0 * INT64_MAX + 0 = 0`
  - But if we use `set(b1, x, y, 1)` with larger y:
  - `index = y * width + x` can overflow again!
  - **Out-of-bounds write to tiny buffer!**

## Testing Further

Let's test with different coordinates to trigger the overflow in `set()`:

```bitscript
bitmap b1 = create(9223372036854775807, 2);
set(b1, 0, 1, 1);  # y=1, index = 1 * INT64_MAX = overflows!
int val = get(b1, 0, 1);
```

This should cause heap corruption!

