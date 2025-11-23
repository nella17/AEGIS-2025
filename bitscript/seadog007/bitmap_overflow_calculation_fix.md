# Bitmap Overflow Calculation - The Real Issue

## The Formula (from bitmap_set)

```c
v8 = a3 * *a1 + a2;  // bit_index = y * width + x
v7 = v8 / 8;         // byte_index = bit_index / 8
result = a1[2] + v7; // target_addr = bitmap_data_ptr + byte_index
```

## The Problem

For `offset = 7464 bytes`:
- `bit_index = offset * 8 = 59712`
- `y * INT64_MAX + x = 59712`

**Solving:**
- `y = 59712 / INT64_MAX = 0` (integer division)
- `x = 59712 % INT64_MAX = 59712` ❌

**But `x` must be < 8!** (bit position within byte)

## The Real Solution

We need to account for the fact that `x` wraps every 8 bits:

**Correct calculation:**
```
bit_index = offset * 8
y = bit_index / (INT64_MAX * 8)  // How many full "rows" of INT64_MAX bytes
x = (bit_index % (INT64_MAX * 8)) % 8  // Bit position within byte
```

Wait, that's still wrong. Let me recalculate:

**Actually:**
```
bit_index = y * INT64_MAX + x
byte_index = bit_index / 8 = (y * INT64_MAX + x) / 8
```

For `byte_index = 7464`:
- `7464 * 8 = 59712` bits
- `y * INT64_MAX + x = 59712`

Since `INT64_MAX = 9223372036854775807`:
- `y = 59712 / 9223372036854775807 = 0`
- `x = 59712 % 9223372036854775807 = 59712`

But `x` is the bit position, and it should be 0-7!

**The issue:** The formula `y * width + x` treats `x` as a bit offset, not a bit position within a byte.

Looking at the code again:
- `v8 = y * width + x` where `x` is the x coordinate (0 to width-1)
- `v7 = v8 / 8` gives byte index
- `v6 = v8 % 8` gives bit position within byte

So `x` can be any value 0 to width-1, and the bit position is `(y * width + x) % 8`.

**For our case:**
- `v8 = 0 * INT64_MAX + 59712 = 59712`
- `v7 = 59712 / 8 = 7464` ✅ (correct byte index!)
- `v6 = 59712 % 8 = 0` ✅ (bit position 0)

So `set(b1, 59712, 0, 1)` should write to `bitmap_data_ptr + 7464`!

**But the bounds check:** `x >= width` will fail if `x = 59712` and `width = INT64_MAX`!

Actually wait, `59712 < INT64_MAX`, so the bounds check passes!

**So the correct call should be:**
```bitscript
set(b1, 59712, 0, 1);  // x=59712, y=0
```

This should write to `bitmap_data_ptr + 7464`!

