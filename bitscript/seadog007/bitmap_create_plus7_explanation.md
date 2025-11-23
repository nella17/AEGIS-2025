# Why `v2 = a2 * a1 + 7` in bitmap_create?

## The Purpose: Ceiling Division (Round Up to Nearest Byte)

The `+ 7` is a **standard technique for rounding up division by 8** when converting bits to bytes.

### The Problem

A bitmap stores data as **bits**, but memory is allocated in **bytes** (8 bits per byte).

- `a2 * a1` = total number of **bits** needed
- We need to convert this to **bytes** for `malloc()`
- But we can't have fractional bytes - we need to **round up**

### The Solution: `(bits + 7) / 8`

**Formula:** `bytes = (bits + 7) / 8`

This is equivalent to: `bytes = ceil(bits / 8)`

### How It Works

The `+ 7` ensures that any partial byte gets rounded up:

**Examples:**
- **1 bit** → `(1 + 7) / 8 = 1` byte ✓
- **7 bits** → `(7 + 7) / 8 = 1` byte ✓
- **8 bits** → `(8 + 7) / 8 = 1` byte ✓ (integer division: 15/8 = 1)
- **9 bits** → `(9 + 7) / 8 = 2` bytes ✓
- **15 bits** → `(15 + 7) / 8 = 2` bytes ✓
- **16 bits** → `(16 + 7) / 8 = 2` bytes ✓

### In the Code

```c
v2 = a2 * a1 + 7;        // bits + 7
v4[2] = malloc((int)(v2 >> 3));  // (bits + 7) / 8
```

- `v2 >> 3` is equivalent to `v2 / 8` (right shift by 3 = divide by 8)
- The `+ 7` ensures we always allocate enough bytes, even for partial bytes

### Why 7 Specifically?

For division by `n`, the formula to round up is: `(value + (n - 1)) / n`

- For `n = 8`: `(value + 7) / 8`
- This works because:
  - If `value` is already divisible by 8: `(8k + 7) / 8 = k` (no change)
  - If `value` has remainder 1-7: `(8k + r + 7) / 8 = k + 1` (rounds up)

### The Overflow Case

```c
if ( v2 < 0 )
    v2 = a2 * a1 + 14;
```

The `+ 14` is likely a **buggy attempt** to handle overflow, but it doesn't make sense:
- If `a2 * a1` overflows to negative, adding 14 won't fix it
- The proper fix would be to check for overflow **before** the multiplication

### In Our Exploit

With `create(9223372036854775807, 2)`:
- `a2 * a1 = 2 * INT64_MAX` → overflows to `-2`
- `v2 = -2 + 7 = 5`
- `malloc((int)(5 >> 3)) = malloc(0)` → **tiny buffer!**

The `+ 7` is correct in normal cases, but when the multiplication overflows, it doesn't help - we still get a tiny allocation.

## Summary

**The `+ 7` is for ceiling division:**
- Converts bits to bytes, rounding up
- Standard technique: `(bits + 7) / 8 = ceil(bits / 8)`
- Ensures we allocate enough memory for partial bytes
- **Not a vulnerability itself** - it's correct code
- **The vulnerability is the missing overflow check** before the multiplication

